from __future__ import annotations

import json
from pathlib import Path

import httpx

from app.config import settings


def load_index_report_summary() -> dict[str, int | str | None]:
    """Read local index_report.json for catalog totals (no network)."""
    try:
        code_root = Path(__file__).resolve().parents[4]
        report_path = code_root / "rag" / "data" / "index_report.json"
        if not report_path.is_file():
            return {"filesTotal": 0, "chunksTotal": 0, "builtAt": None}
        data = json.loads(report_path.read_text(encoding="utf-8"))
        return {
            "filesTotal": int(data.get("files_total", 0)),
            "chunksTotal": int(data.get("chunks_total", 0)),
            "builtAt": data.get("built_at"),
        }
    except Exception:
        return {"filesTotal": 0, "chunksTotal": 0, "builtAt": None}


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
            chunks = int(data.get("chunks", 0) or 0)
            if chunks <= 0:
                report = load_index_report_summary()
                chunks = int(report.get("chunksTotal", 0) or 0)
            return True, "ok", chunks
    except httpx.ConnectError:
        return (
            False,
            f"无法连接 RAG 服务 {base}, 请先运行 code/rag/start-rag.bat",
            0,
        )
    except Exception as exc:
        return False, str(exc), 0
