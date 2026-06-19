from __future__ import annotations

from app.core.rag.base import RagProvider


class StubRagProvider(RagProvider):
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
