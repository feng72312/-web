from __future__ import annotations

import logging

from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider

logger = logging.getLogger(__name__)


async def safe_rag_search(
    query: str,
    *,
    category: str | None = None,
) -> tuple[list[dict[str, str]], str | None]:
    try:
        rag = build_rag_provider()
        rows = normalize_rag_excerpts(await rag.search(query, category=category))
        return rows, None
    except Exception as err:
        logger.warning("rag search failed category=%s: %s", category, err)
        return [], str(err)
