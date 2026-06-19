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
        *,
        authority_tiers: list[str] | None = None,
        evidence_roles: list[str] | None = None,
        library_roles: list[str] | None = None,
        topic_scope: list[str] | None = None,
        classic_whitelist: list[str] | None = None,
        exclude_benchmark: bool = False,
        judge_only: bool = False,
        partitioned: bool = False,
        school_whitelist: list[str] | None = None,
        palace_scope: list[str] | None = None,
        star_scope: list[str] | None = None,
    ) -> list[dict[str, str]]:
        """Return list of {source, excerpt} dicts."""
