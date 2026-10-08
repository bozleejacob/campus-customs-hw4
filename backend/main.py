import hashlib
import hmac
import json
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

from agent import get_chat_reply
from models import ChatReply

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=DATA_DIR), name="media")


# --- Password hashing -------------------------------------------------
#
# New hashes are stored as "pbkdf2_sha256$<iterations>$<salt>$<hex digest>",
# an explicit, self-describing format (PBKDF2-HMAC-SHA256, random salt per
# user) so the iteration count can be raised later without breaking older
# hashes. Pre-existing seed rows in the database use an older 3-part format
# ("pbkdf2_sha256$<salt>$<hex digest>") without a stored iteration count;
# LEGACY_ITERATIONS is our best-effort guess for verifying those.

PBKDF2_ITERATIONS = 600_000
LEGACY_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    parts = stored_hash.split("$")
    if len(parts) == 4:
        algorithm, iterations_str, salt, digest = parts
        iterations = int(iterations_str)
    elif len(parts) == 3:
        algorithm, salt, digest = parts
        iterations = LEGACY_ITERATIONS
    else:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), iterations
    ).hex()
    return hmac.compare_digest(candidate, digest)


class SizeStock(BaseModel):
    size: str
    quantity: int


class ProductSummary(BaseModel):
    product_id: str
    name: str
    garment_type: str
    short_description: str
    price: float
    image_url: str


class ProductDetail(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: List[str]
    price: float
    image_url: str
    sizes: List[SizeStock]
    total_stock: int


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def truncate(text: str, limit: int = 110) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


@app.get("/products", response_model=List[ProductSummary])
def list_products():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    conn.close()
    return [
        ProductSummary(
            product_id=row["product_id"],
            name=row["name"],
            garment_type=row["garment_type"],
            short_description=truncate(row["description"]),
            price=row["price"],
            image_url=f"/media/{row['image_file_path']}",
        )
        for row in rows
    ]


@app.get("/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    size_rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id",
        (product_id,),
    ).fetchall()
    conn.close()

    sizes = [SizeStock(size=r["size"], quantity=r["quantity"]) for r in size_rows]
    return ProductDetail(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        image_url=f"/media/{row['image_file_path']}",
        sizes=sizes,
        total_stock=sum(s.quantity for s in sizes),
    )


# --- Auth ---------------------------------------------------------------


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthUser(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    created_at: str


@app.post("/auth/register", response_model=AuthUser, status_code=201)
def register(payload: RegisterRequest):
    if len(payload.password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters"
        )

    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", (payload.email,)
    ).fetchone()
    if existing is not None:
        conn.close()
        raise HTTPException(status_code=409, detail="An account with that email already exists")

    name = f"{payload.first_name} {payload.last_name}".strip()
    password_hash = hash_password(payload.password)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.execute(
        """
        INSERT INTO users (name, email, password_hash, created_at, first_name, last_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, payload.email, password_hash, created_at, payload.first_name, payload.last_name),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return AuthUser(
        id=user_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        created_at=created_at,
    )


@app.post("/auth/login", response_model=AuthUser)
def login(payload: LoginRequest):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (payload.email,)
    ).fetchone()
    conn.close()

    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return AuthUser(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
        created_at=row["created_at"],
    )


# --- Shop chatbot ---------------------------------------------------------
#
# Chat history is only ever read/written for logged-in shoppers (user_id is
# NOT NULL on chat_messages, which naturally enforces that guests aren't
# persisted). We store mentioned_product_ids (not full product snapshots) in
# products_json, since the frontend already re-fetches live product detail by
# id when displaying cards — storing ids avoids replaying stale prices/stock
# from history.

MAX_HISTORY_MESSAGES = 12  # last ~6 user/assistant turns given as context


class ChatMessageRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    current_product_id: Optional[str] = None


class ChatHistoryEntry(BaseModel):
    role: str
    content: str
    product_ids: List[str]
    created_at: str


@app.post("/chat", response_model=ChatReply)
async def chat(payload: ChatMessageRequest):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    customer_name = None
    customer_email = None
    history_text = None

    conn = get_connection()
    if payload.user_id is not None:
        user_row = conn.execute(
            "SELECT first_name, last_name, email FROM users WHERE id = ?",
            (payload.user_id,),
        ).fetchone()
        if user_row is not None:
            customer_name = (
                f"{user_row['first_name'] or ''} {user_row['last_name'] or ''}".strip() or None
            )
            customer_email = user_row["email"]

            history_rows = conn.execute(
                "SELECT role, content FROM chat_messages WHERE user_id = ? "
                "ORDER BY id DESC LIMIT ?",
                (payload.user_id, MAX_HISTORY_MESSAGES),
            ).fetchall()
            if history_rows:
                turns = [
                    f"{'Shopper' if r['role'] == 'user' else 'You'}: {r['content']}"
                    for r in reversed(history_rows)
                ]
                history_text = "\n".join(turns)
    conn.close()

    # One automatic retry before giving up: transient hiccups (a flaky model
    # response, a brief provider error) shouldn't immediately dead-end the
    # shopper with an apology if trying again would have just worked.
    reply = None
    for attempt in range(2):
        try:
            reply = await get_chat_reply(
                message,
                customer_name=customer_name,
                customer_email=customer_email,
                current_product_id=payload.current_product_id,
                history_text=history_text,
            )
            break
        except Exception:
            if attempt == 1:
                reply = ChatReply(
                    reply="Sorry, I couldn't process that message. Could you rephrase it?",
                    mentioned_product_ids=[],
                )

    if payload.user_id is not None:
        conn = get_connection()
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (payload.user_id, "user", message, None),
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (
                payload.user_id,
                "assistant",
                reply.reply,
                json.dumps(reply.mentioned_product_ids) if reply.mentioned_product_ids else None,
            ),
        )
        conn.commit()
        conn.close()

    return reply


@app.get("/chat/history/{user_id}", response_model=List[ChatHistoryEntry])
def get_chat_history(user_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content, products_json, created_at FROM chat_messages "
        "WHERE user_id = ? ORDER BY id",
        (user_id,),
    ).fetchall()
    conn.close()
    return [
        ChatHistoryEntry(
            role=row["role"],
            content=row["content"],
            product_ids=json.loads(row["products_json"]) if row["products_json"] else [],
            created_at=row["created_at"],
        )
        for row in rows
    ]
