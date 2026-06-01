from __future__ import annotations

from typing import Any

from app.core.interpret.service import InterpretService
from app.core.rag.base import RagProvider


async def fetch_on_demand_rag(
    rag: RagProvider,
    chart: dict[str, Any],
    missing_topics: list[str],
    *,
    top_k: int = 3,
    category: str | None = None,
) -> list[dict[str, str]]:
    if not missing_topics:
        return []
    interpret_service = InterpretService()
    query = interpret_service.build_query(chart)
    if "tiaohou" in missing_topics:
        query = f"{query} 调候 用神 喜忌"
    rows = await rag.search(query, top_k=top_k, category=category)
    return rows
