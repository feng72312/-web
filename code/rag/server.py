"""Local semantic search HTTP service for bazi classics."""

from __future__ import annotations

from typing import Any

import chromadb
import uvicorn
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL, HOST, PORT

app = FastAPI(title="Bazi Local RAG", version="1.0.0")

_collection = None


def get_collection():
    global _collection
    if _collection is not None:
        return _collection

    if not CHROMA_DIR.exists():
        raise RuntimeError(f"index not found, run build_index.py first: {CHROMA_DIR}")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    _collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )
    return _collection


class SearchRequest(BaseModel):
    query: str
    topK: int = Field(default=5, ge=1, le=20)


class SearchHit(BaseModel):
    source: str
    excerpt: str
    score: float | None = None


@app.get("/health")
def health() -> dict[str, Any]:
    try:
        collection = get_collection()
        count = collection.count()
        return {"status": "ok", "chunks": count, "model": EMBED_MODEL}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@app.post("/search")
def search(body: SearchRequest) -> list[dict[str, Any]]:
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    try:
        collection = get_collection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    result = collection.query(
        query_texts=[query],
        n_results=body.topK,
        include=["documents", "metadatas", "distances"],
    )

    hits: list[dict[str, Any]] = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for doc, meta, distance in zip(docs, metas, distances):
        source = meta.get("source") or meta.get("file_name") or "unknown"
        score = None
        if distance is not None:
            score = round(1.0 - float(distance), 4)
        hits.append(
            {
                "source": str(source),
                "excerpt": doc,
                "score": score,
            }
        )

    return hits


if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=False)
