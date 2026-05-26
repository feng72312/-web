from __future__ import annotations

from app.core.rag.base import RagProvider


class StubRagProvider(RagProvider):
    async def search(self, query: str, top_k: int = 5) -> list[dict[str, str]]:
        return [
            {
                "source": "stub",
                "excerpt": (
                    "RAG provider is in stub mode. Connect eyelevel-rag via HTTP "
                    "or add an MCP bridge, then set BAZI_RAG_PROVIDER=http."
                ),
            }
        ]
