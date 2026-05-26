from __future__ import annotations

from abc import ABC, abstractmethod


class RagProvider(ABC):
    """Abstract RAG backend. Swap stub/http/mcp-bridge without changing callers."""

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> list[dict[str, str]]:
        """Return list of {source, excerpt} dicts."""
