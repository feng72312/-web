from __future__ import annotations

import httpx

from app.core.rag.base import RagProvider


class HttpRagProvider(RagProvider):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

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
        payload: dict[str, object] = {"query": query, "topK": top_k}
        if category:
            payload["category"] = category
        if authority_tiers:
            payload["authorityTiers"] = authority_tiers
        if evidence_roles:
            payload["evidenceRoles"] = evidence_roles
        if library_roles:
            payload["libraryRoles"] = library_roles
        if topic_scope:
            payload["topicScope"] = topic_scope
        if classic_whitelist:
            payload["classicWhitelist"] = classic_whitelist
        if exclude_benchmark:
            payload["excludeBenchmark"] = True
        if judge_only:
            payload["judgeOnly"] = True
        if partitioned:
            payload["partitioned"] = True
        if school_whitelist:
            payload["schoolWhitelist"] = school_whitelist
        if palace_scope:
            payload["palaceScope"] = palace_scope
        if star_scope:
            payload["starScope"] = star_scope
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"无法连接 RAG 服务 {self.base_url}, 请先启动 code/rag/start-rag.bat"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"RAG 服务返回错误 {exc.response.status_code}: {exc.response.text[:200]}"
            ) from exc

        if isinstance(data, str):
            return [{"source": "http", "excerpt": data}]
        if isinstance(data, list):
            rows: list[dict[str, str]] = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                excerpt = item.get("excerpt") or item.get("document") or ""
                if not excerpt:
                    continue
                row = {
                    "source": str(item.get("source", "unknown")),
                    "excerpt": str(excerpt),
                }
                for key in (
                    "classic",
                    "chapter",
                    "dynasty",
                    "author",
                    "score",
                    "rerankScore",
                    "authorityTier",
                    "evidenceRole",
                    "sourceType",
                    "libraryRole",
                    "canJudge",
                    "judgmentPolicy",
                    "domains",
                    "evidenceBucket",
                    "fileName",
                    "topicScope",
                    "textRole",
                    "caseOnly",
                    "school",
                    "palaceScope",
                    "starScope",
                ):
                    value = item.get(key)
                    if value not in (None, ""):
                        row[key] = (
                            str(value)
                            if key
                            in {
                                "classic",
                                "chapter",
                                "dynasty",
                                "author",
                                "authorityTier",
                                "evidenceRole",
                                "sourceType",
                                "libraryRole",
                                "judgmentPolicy",
                                "domains",
                                "evidenceBucket",
                                "fileName",
                                "topicScope",
                                "textRole",
                                "school",
                                "palaceScope",
                                "starScope",
                            }
                            else value
                        )
                if item.get("caseOnly") is True:
                    row["caseOnly"] = True
                rows.append(row)
            return rows
        if isinstance(data, dict) and "result" in data:
            return [{"source": "http", "excerpt": str(data["result"])}]
        raise RuntimeError("RAG 服务返回了无法识别的数据格式")
