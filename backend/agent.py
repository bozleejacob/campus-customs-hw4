"""PydanticAI agent entry point for the Campus Customs shop chatbot."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from models import ChatReply
from tools import AUDIT_LOG_PATH, get_product_stock, run_agent_with_audit, search_products

ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompts" / "prompt.md"

MODEL_NAME = "gpt-5.6-luna"

# Caps how many tool calls the agent can make while answering a single chat
# message, as a safety net against a runaway tool-calling loop (cost and
# latency control, not expected to be hit in normal use — search + one or
# two stock lookups + an alternative search covers the out-of-stock case).
MAX_TOOL_CALLS_PER_TURN = 6

load_dotenv()


def build_model() -> OpenAIResponsesModel:
    api_key = os.environ["PORTKEY_API_KEY"]
    provider = OpenAIProvider(base_url="https://api.portkey.ai/v1", api_key=api_key)
    return OpenAIResponsesModel(MODEL_NAME, provider=provider)


def build_chat_agent(model: OpenAIResponsesModel) -> Agent:
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    async def search_products_tool(query: str) -> list[dict]:
        """Search the product catalogue for items matching a free-text query
        (e.g. 'yale hoodie', 'baseball crewneck'). Returns up to 8 candidates
        with product_id, name, garment type, price, and a short description.
        """
        return [p.model_dump() for p in search_products(query)]

    async def get_product_stock_tool(product_id: str) -> dict | None:
        """Look up full description, price, colors, and current size/stock
        for one product by its product_id (from a prior search_products result).
        Returns None if the product_id doesn't exist.
        """
        detail = get_product_stock(product_id)
        return detail.model_dump() if detail else None

    return Agent(
        model,
        output_type=ChatReply,
        system_prompt=system_prompt,
        tools=[search_products_tool, get_product_stock_tool],
    )


_agent: Agent | None = None


def get_agent() -> Agent:
    """Build the chat agent once and reuse it across requests."""
    global _agent
    if _agent is None:
        _agent = build_chat_agent(build_model())
    return _agent


def _build_prompt(
    message: str,
    customer_name: str | None,
    customer_email: str | None,
    current_product_id: str | None,
    history_text: str | None,
) -> str:
    """Prepend customer identity, page context, and recent history (when known)
    as plain context lines ahead of the shopper's new message. Keeping this as
    text context (rather than reconstructing PydanticAI message history) is
    simpler and enough for the agent to use the information naturally.
    """
    context_lines = []

    if customer_name or customer_email:
        who = customer_name or "this shopper"
        context_lines.append(
            f"You are chatting with {who} (email: {customer_email or 'unknown'}). "
            "You may use their name naturally; don't overuse it."
        )

    if current_product_id:
        context_lines.append(
            f"Page context: the shopper is currently viewing the product page for "
            f"product_id={current_product_id!r}. If they refer to 'this', 'it', or "
            "similar without naming an item, assume they mean this product and call "
            "get_product_stock with this id."
        )

    if history_text:
        context_lines.append(f"Recent conversation history with this shopper:\n{history_text}")

    if not context_lines:
        return message

    return "\n\n".join(context_lines) + f"\n\nShopper's new message: {message}"


async def get_chat_reply(
    message: str,
    customer_name: str | None = None,
    customer_email: str | None = None,
    current_product_id: str | None = None,
    history_text: str | None = None,
) -> ChatReply:
    agent = get_agent()
    prompt = _build_prompt(message, customer_name, customer_email, current_product_id, history_text)
    result = await run_agent_with_audit(
        agent,
        prompt,
        AUDIT_LOG_PATH,
        usage_limits=UsageLimits(tool_calls_limit=MAX_TOOL_CALLS_PER_TURN),
    )
    return result.output
