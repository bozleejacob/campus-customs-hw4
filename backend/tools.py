"""Agent tools / helper functions for the Campus Customs shop chatbot."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, ThinkingPart, ToolCallPart, ToolReturnPart

from models import AuditEntry, ProductHit, ProductStockDetail, SizeStock

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campus_customs.db"

MAX_SEARCH_RESULTS = 8


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _truncate(text: str, limit: int = 110) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def search_products(query: str, limit: int = MAX_SEARCH_RESULTS) -> list[ProductHit]:
    """Search the whole catalogue at once (no per-item AI calls) for products
    whose name, garment type, description, or search tags match the query
    text. Returns at most `limit` results (capped at MAX_SEARCH_RESULTS),
    ranked by simple keyword overlap.
    """
    limit = min(limit, MAX_SEARCH_RESULTS)
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM catalogue").fetchall()
    conn.close()

    needles = [w.lower() for w in query.split() if w]

    def score(row: sqlite3.Row) -> int:
        haystack = " ".join(
            [row["name"], row["garment_type"], row["description"], row["search_tags"]]
        ).lower()
        return sum(haystack.count(n) for n in needles)

    scored = sorted(rows, key=score, reverse=True)
    top = [r for r in scored if score(r) > 0][:limit]

    return [
        ProductHit(
            product_id=r["product_id"],
            name=r["name"],
            garment_type=r["garment_type"],
            price=r["price"],
            short_description=_truncate(r["description"]),
        )
        for r in top
    ]


def get_product_stock(product_id: str) -> ProductStockDetail | None:
    """Look up full detail plus current size/stock for one product by its
    product_id (as returned by search_products). Returns None if the id
    doesn't exist, rather than guessing.
    """
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
    ).fetchone()
    if row is None:
        conn.close()
        return None

    size_rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id",
        (product_id,),
    ).fetchall()
    conn.close()

    sizes = [
        SizeStock(size=s["size"], quantity=s["quantity"], in_stock=s["quantity"] > 0)
        for s in size_rows
    ]
    return ProductStockDetail(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        sizes=sizes,
        total_stock=sum(s.quantity for s in sizes),
    )


# --- Audit trail -------------------------------------------------------------

AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
AUDIT_SUMMARY_MAX_CHARS = 300


def _truncate_summary(text: str, limit: int = AUDIT_SUMMARY_MAX_CHARS) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _append_audit_entry(entry: AuditEntry, audit_path: Path = AUDIT_LOG_PATH) -> None:
    """Append one entry to audit_path, preserving whatever's already there.
    Never wipes the file — each run's entries add to what's there.
    """
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if audit_path.exists():
        with open(audit_path, encoding="utf-8") as f:
            existing = json.load(f)
    existing.append(entry.model_dump())
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


async def run_agent_with_audit(agent: Agent, user_prompt: str, audit_path: Path = AUDIT_LOG_PATH, **run_kwargs):
    """Run the agent, and append one AuditEntry per model turn (one per tool
    call within a turn that made tool calls) to audit_path as they're
    processed.
    """
    run_id = str(uuid.uuid4())
    prev_time = datetime.now(timezone.utc)

    result = await agent.run(user_prompt, **run_kwargs)
    messages = result.all_messages()

    tool_returns: dict[str, str] = {}
    for msg in messages:
        if isinstance(msg, ModelRequest):
            for part in msg.parts:
                if isinstance(part, ToolReturnPart):
                    content = (
                        part.content if isinstance(part.content, str) else json.dumps(part.content, default=str)
                    )
                    tool_returns[part.tool_call_id] = _truncate_summary(content)

    iteration = 0
    for msg in messages:
        if not isinstance(msg, ModelResponse):
            continue

        thoughts = (
            "\n".join(
                part.content for part in msg.parts if isinstance(part, (TextPart, ThinkingPart)) and part.content
            )
            or None
        )
        think_time_seconds = (msg.timestamp - prev_time).total_seconds()
        prev_time = msg.timestamp
        stop_reason = str(msg.finish_reason) if msg.finish_reason else None
        tool_calls = [part for part in msg.parts if isinstance(part, ToolCallPart)]

        calls_to_log = tool_calls or [None]
        for call in calls_to_log:
            entry = AuditEntry(
                run_id=run_id,
                iteration=iteration,
                timestamp=msg.timestamp.isoformat(),
                think_time_seconds=think_time_seconds,
                thoughts=thoughts,
                tool_name=call.tool_name if call else None,
                tool_args=call.args_as_dict() if call else None,
                tool_result_summary=tool_returns.get(call.tool_call_id) if call else None,
                stop_reason=stop_reason,
            )
            _append_audit_entry(entry, audit_path)
            iteration += 1

    return result
