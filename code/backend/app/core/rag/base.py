from __future__ import annotations

from abc import ABC, abstractmethod


def normalize_rag_excerpts(excerpts: list[dict[str, str]]) -> list[dict[str, str]]:
    """Stub means no classics index; allow AI-only interpret on CloudRun."""
    if len(excerpts) == 1 and excerpts[0].get("source") == "stub":
        return []
    return excerpts


class RagProvider(ABC):
    """Abstract RAG backend. Swap stub/http/mcp-bridge without changing callers."""

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
    ) -> list[dict[str, str]]:
        """Return list of {source, excerpt} dicts."""
