from __future__ import annotations

import httpx

from app.config import settings


async def probe_rag_service() -> tuple[bool, str, int]:
    if settings.rag_provider != "http" or not settings.rag_http_url.strip():
        return (
            False,
            "backend 未配置 HTTP RAG, 请在 backend/.env 设置 BAZI_RAG_PROVIDER=http",
            0,
        )

    base = settings.rag_http_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(f"{base}/health")
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "ok":
                return False, str(data.get("message", "rag unhealthy")), 0
            chunks = int(data.get("chunks", 0))
            return True, "ok", chunks
    except httpx.ConnectError:
        return (
            False,
            f"无法连接 RAG 服务 {base}, 请先运行 code/rag/start-rag.bat",
            0,
        )
    except Exception as exc:
        return False, str(exc), 0
