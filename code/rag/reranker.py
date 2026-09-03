from __future__ import annotations

import os
from typing import Any

_reranker = None


def rerank_enabled() -> bool:
    return os.environ.get("RAG_RERANK", "0").strip().lower() in {"1", "true", "yes", "on"}


def rerank_model_name() -> str:
    return os.environ.get("RAG_RERANK_MODEL", "BAAI/bge-reranker-base")


def get_reranker():
    global _reranker
    if _reranker is not None:
        return _reranker
    if not rerank_enabled():
        return None

    from sentence_transformers import CrossEncoder
    from config import resolve_device

    _reranker = CrossEncoder(rerank_model_name(), device=resolve_device())
    return _reranker


def rerank_hits(query: str, hits: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    if not hits or top_k <= 0:
        return hits

    model = get_reranker()
    if model is None:
        return hits[:top_k]

    pairs = [(query, str(item.get("excerpt") or "")) for item in hits]
    scores = model.predict(pairs)
    ranked = list(zip(hits, scores))
    ranked.sort(key=lambda pair: float(pair[1]), reverse=True)

    output: list[dict[str, Any]] = []
    for item, score in ranked[:top_k]:
        merged = dict(item)
        merged["rerankScore"] = round(float(score), 4)
        output.append(merged)
    return output
