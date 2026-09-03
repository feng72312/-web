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
from config import CHROMA_DIR, CHROMA_SETTINGS, DEFAULT_RAG_COLLECTION, EMBED_MODEL, SOURCE_DIR, resolve_device
from reranker import rerank_enabled, rerank_hits

AUTHORITY_WEIGHT = {"S": 1.0, "A": 0.75, "B": 0.45, "C": 0.2, "D": 0.05}
TEXT_ROLE_WEIGHT = {
    "original": 1.0,
    "commentary": 0.95,
    "annotation": 0.9,
    "case": 0.7,
    "toc": 0.3,
    "editor_note": 0.2,
}
EVIDENCE_BUCKET = {
    "primary_judge": "primaryEvidence",
    "primary_classic": "primaryEvidence",
    "star_judge": "primaryEvidence",
    "pattern_judge": "primaryEvidence",
    "star_palace_judge": "primaryEvidence",
    "systematic_support": "secondaryEvidence",
    "palace_topic_support": "secondaryEvidence",
    "mutagen_judge": "secondaryEvidence",
    "limit_judge": "secondaryEvidence",
    "tiaohou_judge": "primaryEvidence",
    "geju_judge": "primaryEvidence",
    "qishi_judge": "primaryEvidence",
    "shishen_judge": "primaryEvidence",
    "suiyun_judge": "primaryEvidence",
    "core_divination_judge": "primaryEvidence",
    "classic_topic_judge": "primaryEvidence",
    "encyclopedic_judge": "primaryEvidence",
    "early_source_support": "secondaryEvidence",
    "method_support": "secondaryEvidence",
    "yijing_divination_support": "secondaryEvidence",
    "case_formula_support": "secondaryEvidence",
    "secondary_support": "secondaryEvidence",
    "modern_explanation": "secondaryEvidence",
    "modern_image_support": "modernSupport",
    "modern_mixed_support": "modernSupport",
    "modern_method_support": "modernSupport",
    "case_reference": "caseReference",
    "low_trust": "excludedOrLowTrust",
}

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
            settings=CHROMA_SETTINGS or Settings(anonymized_telemetry=False),
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
    _embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL,
        device=resolve_device(),
    )
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
        authority_tier = str(meta.get("authorityTier") or "D")
        evidence_role = str(meta.get("evidenceRole") or "low_trust")
        library_role = str(meta.get("libraryRole") or "supplement_library")
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
                "authorityTier": authority_tier,
                "evidenceRole": evidence_role,
                "sourceType": str(meta.get("sourceType") or ""),
                "libraryRole": library_role,
                "canJudge": meta.get("canJudge") == "1",
                "judgmentPolicy": str(meta.get("judgmentPolicy") or ""),
                "domains": str(meta.get("domains") or ""),
                "topicScope": str(meta.get("topicScope") or ""),
                "textRole": str(meta.get("textRole") or "original"),
                "school": str(meta.get("school") or "general"),
                "palaceScope": str(meta.get("palaceScope") or ""),
                "starScope": str(meta.get("starScope") or ""),
                "caseOnly": meta.get("caseOnly") == "1",
                "evidenceBucket": EVIDENCE_BUCKET.get(evidence_role, "excludedOrLowTrust"),
            }
        )
    return hits


def _passes_filters(hit: dict[str, Any], body: Any) -> bool:
    if getattr(body, "excludeBenchmark", False):
        name = str(hit.get("fileName") or "").lower()
        if "contest" in name or "命理师大赛" in name:
            return False

    authority_tiers = getattr(body, "authorityTiers", None) or []
    if authority_tiers and hit.get("authorityTier") not in authority_tiers:
        return False

    evidence_roles = getattr(body, "evidenceRoles", None) or []
    if evidence_roles and hit.get("evidenceRole") not in evidence_roles:
        return False

    library_roles = getattr(body, "libraryRoles", None) or []
    if library_roles and hit.get("libraryRole") not in library_roles:
        return False

    classic_whitelist = getattr(body, "classicWhitelist", None) or []
    if classic_whitelist:
        classic = str(hit.get("classic") or "")
        if classic and classic not in classic_whitelist:
            return False

    topic_scope = getattr(body, "topicScope", None) or []
    if topic_scope:
        domains = str(hit.get("domains") or "")
        scope = str(hit.get("topicScope") or "")
        merged = f"{domains},{scope}"
        if merged and not any(t in merged for t in topic_scope):
            return False

    if getattr(body, "judgeOnly", False) and not hit.get("canJudge"):
        return False

    school_whitelist = getattr(body, "schoolWhitelist", None) or []
    if school_whitelist:
        hit_school = str(hit.get("school") or "general")
        allowed = set(school_whitelist) | {"general"}
        if hit_school not in allowed:
            return False

    palace_scope = getattr(body, "palaceScope", None) or []
    if palace_scope:
        hit_scope = str(hit.get("palaceScope") or "")
        if hit_scope and not any(token in hit_scope for token in palace_scope):
            return False

    star_scope = getattr(body, "starScope", None) or []
    if star_scope:
        hit_scope = str(hit.get("starScope") or "")
        if hit_scope and not any(token in hit_scope for token in star_scope):
            return False

    return True


def _weighted_score(hit: dict[str, Any]) -> float:
    base = hit.get("rerankScore")
    if base is None:
        base = hit.get("score") or 0.0
    tier = str(hit.get("authorityTier") or "D")
    role = str(hit.get("textRole") or "original")
    score = (
        float(base)
        * AUTHORITY_WEIGHT.get(tier, 0.05)
        * TEXT_ROLE_WEIGHT.get(role, 0.85)
    )
    if hit.get("caseOnly"):
        score *= 0.55
    return score


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

    filtered = [h for h in merged if _passes_filters(h, body)]

    if rerank_enabled():
        ranked = rerank_hits(query, filtered, min(len(filtered), body.topK * 3))
        ranked = sorted(ranked, key=_weighted_score, reverse=True)
    else:
        ranked = sorted(filtered, key=_weighted_score, reverse=True)

    if getattr(body, "partitioned", False):
        buckets: dict[str, list[dict[str, Any]]] = {
            "primaryEvidence": [],
            "secondaryEvidence": [],
            "caseReference": [],
            "excludedOrLowTrust": [],
        }
        for hit in ranked:
            bucket = str(hit.get("evidenceBucket") or "excludedOrLowTrust")
            if bucket not in buckets:
                bucket = "excludedOrLowTrust"
            if len(buckets[bucket]) < body.topK:
                buckets[bucket].append(hit)
        return buckets  # type: ignore[return-value]

    return ranked[: body.topK]
