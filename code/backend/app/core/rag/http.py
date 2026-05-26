from __future__ import annotations

import httpx

from app.core.rag.base import RagProvider


class HttpRagProvider(RagProvider):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, str]]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={"query": query, "topK": top_k},
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, str):
                return [{"source": "http", "excerpt": data}]
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "result" in data:
                return [{"source": "http", "excerpt": str(data["result"])}]
            return [{"source": "http", "excerpt": str(data)}]
