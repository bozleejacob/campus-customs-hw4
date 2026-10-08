"""Pydantic / PydanticAI structured types for the Campus Customs shop chatbot.

Grows over time: add one model per new agent ability, plus whatever
supporting types that ability's tools need.
"""

from typing import Optional

from pydantic import BaseModel, Field


# --- Catalogue lookups (used by agent tools) --------------------------------


class SizeStock(BaseModel):
    """Stock on hand for one size of a product."""

    size: str = Field(description="Size label, e.g. 'S', 'M', 'XL'.")
    quantity: int = Field(description="Units currently in stock for this size.")
    in_stock: bool = Field(
        description=(
            "Whether this size currently has any stock (quantity > 0). Computed here, "
            "not left for the agent to infer from the number, so it's never misread."
        )
    )


class ProductHit(BaseModel):
    """One product catalogue search result."""

    product_id: str = Field(description="Stable id used to look up full product detail.")
    name: str = Field(description="Product name.")
    garment_type: str = Field(description="Garment type, e.g. 'hoodie', 'T-shirt'.")
    price: float = Field(description="Price in US dollars.")
    short_description: str = Field(description="Short visual description of the product.")


class ProductStockDetail(BaseModel):
    """Full product detail plus current size/stock, for one product."""

    product_id: str = Field(description="Stable product id.")
    name: str = Field(description="Product name.")
    garment_type: str = Field(description="Garment type, e.g. 'hoodie', 'T-shirt'.")
    description: str = Field(description="Full product description.")
    colors: list[str] = Field(description="Dominant color(s) of the garment.")
    price: float = Field(description="Price in US dollars.")
    sizes: list[SizeStock] = Field(description="Stock on hand, broken down by size.")
    total_stock: int = Field(description="Total units on hand across all sizes.")


# --- Shop chatbot ability ----------------------------------------------------


class ChatReply(BaseModel):
    """Result of answering one shopper chat message."""

    reply: str = Field(description="The chatbot's natural-language reply to the shopper.")
    mentioned_product_ids: list[str] = Field(
        default_factory=list,
        description=(
            "product_id values for any products specifically recommended or referenced in "
            "this reply, in the order mentioned. Empty if no specific products came up."
        ),
    )


# --- Audit trail -------------------------------------------------------------


class AuditEntry(BaseModel):
    """One agent-loop iteration (a model turn, or a single tool call within a
    turn), recorded for later auditing. Appended to output/audit_trail.json.
    """

    run_id: str = Field(description="Groups all iterations that belong to the same agent.run() call.")
    iteration: int = Field(description="Index of this iteration within the run, starting at 0.")
    timestamp: str = Field(description="ISO timestamp when this iteration's model response was received.")
    think_time_seconds: float = Field(
        description=(
            "Wall-clock seconds since the previous iteration (or run start). Includes model "
            "latency and, between iterations, any tool execution time in between."
        )
    )
    thoughts: Optional[str] = Field(
        default=None, description="Reasoning/text content the model produced this turn, if any."
    )
    tool_name: Optional[str] = Field(default=None, description="Name of the tool called this iteration, if any.")
    tool_args: Optional[dict] = Field(default=None, description="Arguments passed to the tool call, if any.")
    tool_result_summary: Optional[str] = Field(
        default=None, description="Short (truncated) summary of what the tool returned, if a tool was called."
    )
    stop_reason: Optional[str] = Field(
        default=None, description="Why the model stopped generating this turn, e.g. 'tool_call', 'stop'."
    )
