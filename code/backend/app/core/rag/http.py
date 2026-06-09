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
    ) -> list[dict[str, str]]:
        payload: dict[str, object] = {"query": query, "topK": top_k}
        if category:
            payload["category"] = category
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
                for key in ("classic", "chapter", "dynasty", "author", "score", "rerankScore"):
                    value = item.get(key)
                    if value not in (None, ""):
                        row[key] = str(value) if key in {"classic", "chapter", "dynasty", "author"} else value
                rows.append(row)
            return rows
        if isinstance(data, dict) and "result" in data:
            return [{"source": "http", "excerpt": str(data["result"])}]
        raise RuntimeError("RAG 服务返回了无法识别的数据格式")
