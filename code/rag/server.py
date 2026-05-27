"""Thin HTTP entrypoint; heavy imports happen in bazi_rag_engine on first use."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Bazi Local RAG", version="2.0.0")

_ENGINE = None


def _load_engine():
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    path = Path(__file__).resolve().with_name("bazi_rag_engine.py")
    spec = importlib.util.spec_from_file_location("bazi_rag_engine_local", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing engine file: {path}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _ENGINE = mod
    return mod


class SearchRequest(BaseModel):
    query: str
    topK: int = Field(default=5, ge=1, le=20)
    category: str | None = None
    categories: list[str] | None = None


@app.get("/ping")
def ping() -> dict[str, Any]:
    import config

    return {
        "status": "ok",
        "chromaDir": str(config.CHROMA_DIR),
        "chromaExists": config.CHROMA_DIR.exists(),
        "engineFile": str(Path(__file__).resolve().with_name("bazi_rag_engine.py")),
    }


@app.get("/health")
def health() -> dict[str, Any]:
    try:
        engine = _load_engine()
        return engine.health()
    except Exception as exc:
        import traceback

        return {
            "status": "error",
            "message": str(exc),
            "errorType": type(exc).__name__,
            "trace": traceback.format_exc()[-1200:],
        }


@app.get("/collections")
def collections() -> dict[str, Any]:
    try:
        engine = _load_engine()
        return {"collections": engine.list_available_collections()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/search")
def search(body: SearchRequest) -> list[dict[str, Any]]:
    try:
        engine = _load_engine()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"engine load failed: {exc}") from exc

    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    try:
        return engine.search(body)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    from config import HOST, PORT

    uvicorn.run("server:app", host=HOST, port=PORT, reload=False)
