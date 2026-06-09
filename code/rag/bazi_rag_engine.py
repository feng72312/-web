"""Heavy RAG logic loaded on first request."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from categories import (
    COLLECTION_TO_FOLDER,
    FOLDER_TO_COLLECTION,
    list_category_dirs,
    resolve_category,
)
from config import CHROMA_DIR, DEFAULT_RAG_COLLECTION, EMBED_MODEL, SOURCE_DIR
from reranker import rerank_enabled, rerank_hits

_client = None
_embedding_fn = None
_collections: dict[str, Any] = {}


def _migrate_legacy_chroma_config() -> None:
    db_path = CHROMA_DIR / "chroma.sqlite3"
    if not db_path.exists():
        return

    default_cfg = {
        "_type": "CollectionConfigurationInternal",
        "hnsw_configuration": {
            "_type": "HNSWConfigurationInternal",
            "space": "cosine",
        },
    }
    payload = json.dumps(default_cfg, ensure_ascii=False)

    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute("SELECT id, config_json_str FROM collections").fetchall()
        for collection_id, config_json_str in rows:
            raw = (config_json_str or "").strip()
            if not raw or raw == "{}":
                conn.execute(
                    "UPDATE collections SET config_json_str = ? WHERE id = ?",
                    (payload, collection_id),
                )
        conn.commit()
    finally:
        conn.close()


def get_client():
    global _client, _embedding_fn
    if _client is not None:
        return _client, _embedding_fn

    if not CHROMA_DIR.exists():
        raise RuntimeError(f"index not found, run build_index.py first: {CHROMA_DIR}")

    try:
        import pysqlite3  # type: ignore

        import sys

        sys.modules["sqlite3"] = pysqlite3
    except ImportError:
        pass

    import chromadb
    from chromadb.config import Settings
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    _migrate_legacy_chroma_config()

    try:
        _client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        _client.heartbeat()
    except Exception as exc:
        msg = str(exc)
        if "tenant" in msg.lower():
            raise RuntimeError(
                "Chroma 索引与 chromadb 版本不兼容. "
                "请在 code/rag 目录执行: py -3.10 -m pip install chromadb==0.5.23 "
                "然后删除 data/chroma 并重新运行 build_index.py"
            ) from exc
        raise
    _embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return _client, _embedding_fn


def get_collection(collection_id: str):
    if collection_id in _collections:
        return _collections[collection_id]

    client, embedding_fn = get_client()
    try:
        coll = client.get_collection(name=collection_id, embedding_function=embedding_fn)
    except Exception as exc:
        raise KeyError(
            f"collection {collection_id} not found, run build_index.py for this category"
        ) from exc
    _collections[collection_id] = coll
    return coll


def list_available_collections() -> list[dict[str, Any]]:
    client, _ = get_client()
    items: list[dict[str, Any]] = []
    for coll in client.list_collections():
        name = coll.name
        folder = COLLECTION_TO_FOLDER.get(name, name)
        try:
            count = client.get_collection(name).count()
        except Exception:
            count = 0
        items.append({"collection": name, "category": folder, "chunks": count})
    return sorted(items, key=lambda x: x["category"])


def health() -> dict[str, Any]:
    try:
        get_client()
        collections = list_available_collections()
        total = sum(item["chunks"] for item in collections)
        return {
            "status": "ok",
            "chunks": total,
            "model": EMBED_MODEL,
            "collections": collections,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "errorType": type(exc).__name__,
        }


def _search_one(collection_id: str, query: str, top_k: int) -> list[dict[str, Any]]:
    collection = get_collection(collection_id)
    result = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    hits: list[dict[str, Any]] = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for doc, meta, distance in zip(docs, metas, distances):
        classic = str(meta.get("classic") or "")
        chapter = str(meta.get("chapter") or "")
        dynasty = str(meta.get("dynasty") or "")
        author = str(meta.get("author") or "")
        file_name = str(meta.get("file_name") or meta.get("source") or "unknown")
        if classic and chapter:
            display_source = f"《{classic}》{chapter}"
        elif classic:
            display_source = f"《{classic}》"
        else:
            display_source = file_name

        category = meta.get("category") or COLLECTION_TO_FOLDER.get(collection_id, "")
        score = round(1.0 - float(distance), 4) if distance is not None else None
        hits.append(
            {
                "source": display_source,
                "excerpt": doc,
                "score": score,
                "rerankScore": None,
                "category": str(category),
                "collection": collection_id,
                "classic": classic,
                "chapter": chapter,
                "dynasty": dynasty,
                "author": author,
                "fileName": file_name,
            }
        )
    return hits


def search(body: Any) -> list[dict[str, Any]]:
    query = body.query.strip()
    if not query:
        raise ValueError("query is required")

    if body.categories:
        target = [resolve_category(c) for c in body.categories]
    elif body.category:
        target = [resolve_category(body.category)]
    else:
        target = [item["collection"] for item in list_available_collections()]
        if not target:
            target = [DEFAULT_RAG_COLLECTION]

    per_collection_k = body.topK
    if rerank_enabled():
        per_collection_k = min(max(body.topK * 3, body.topK), 15)

    merged: list[dict[str, Any]] = []
    for collection_id in target:
        try:
            merged.extend(_search_one(collection_id, query, per_collection_k))
        except Exception:
            continue

    if rerank_enabled():
        return rerank_hits(query, merged, body.topK)

    merged.sort(key=lambda item: item.get("score") or 0, reverse=True)
    return merged[: body.topK]
