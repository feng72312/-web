from __future__ import annotations

from app.core.rag.base import RagProvider


class StubRagProvider(RagProvider):
    async def search(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
    ) -> list[dict[str, str]]:
        return [
            {
                "source": "stub",
                "excerpt": (
                    "当前为演示模式 (未连接典籍库). "
                    "请启动 RAG 服务 (code/rag/start-rag.bat) 并确认 backend/.env 中 "
                    "BAZI_RAG_PROVIDER=http 与 BAZI_RAG_HTTP_URL=http://127.0.0.1:8100, "
                    "然后重启后端."
                ),
            }
        ]
