"""Build per-category Chroma indexes under 数据库/."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from categories import folder_to_collection, list_category_dirs
from chunker import TextChunk, chunk_document, infer_case_only, infer_text_role, infer_topic_scope_hint
from metadata_parser import parse_filename
from config import (
    ALLOWED_SUFFIXES,
    CHROMA_DIR,
    CHROMA_SETTINGS,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_DIR,
    EMBED_MODEL,
    SOURCE_DIR,
    resolve_device,
)
from doc_reader import read_document, read_txt, normalize_text
from source_manifest_loader import lookup_file_meta


def iter_source_files(category_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(category_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            continue
        if "ocr" in path.parts:
            continue
        if "_doc_backup" in path.parts:
            continue
        files.append(path)
    return files


def source_rel(path: Path) -> str:
    return str(path.relative_to(SOURCE_DIR))


def write_report(report_path: Path, summary: dict) -> None:
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def add_chunks(
    collection,
    *,
    rel: str,
    file_name: str,
    category: str,
    collection_id: str,
    book_meta: dict[str, str],
    file_manifest: dict[str, str | bool | list[str]],
    chunks: list[TextChunk],
) -> None:
    batch_size = 64
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str | int]] = []
    classic = str(file_manifest.get("classic") or book_meta.get("classic", ""))

    for index, chunk in enumerate(chunks):
        ids.append(str(uuid.uuid4()))
        documents.append(chunk.text)
        domains = file_manifest.get("domains") or []
        topic_scope = file_manifest.get("topicScope") or []
        if isinstance(topic_scope, str):
            topic_scope_list = [part.strip() for part in topic_scope.split(",") if part.strip()]
        else:
            topic_scope_list = list(topic_scope) if isinstance(topic_scope, list) else []
        text_role = infer_text_role(chunk.text, chunk.chapter)
        judgment_policy = str(file_manifest.get("judgmentPolicy") or "")
        school = str(file_manifest.get("school") or "general")
        palace_scope = file_manifest.get("palaceScope") or []
        star_scope = file_manifest.get("starScope") or []
        mutagen_scope = file_manifest.get("mutagenScope") or []
        limit_scope = file_manifest.get("limitScope") or []

        def _scope_csv(value) -> str:
            if isinstance(value, list):
                return ",".join(str(v) for v in value if v)
            return str(value or "")

        metadatas.append(
            {
                "source": rel,
                "chunk_index": index,
                "file_name": file_name,
                "category": category,
                "collection": collection_id,
                "classic": classic,
                "dynasty": book_meta.get("dynasty", ""),
                "author": book_meta.get("author", ""),
                "chapter": chunk.chapter or "",
                "authorityTier": str(file_manifest.get("authorityTier") or "D"),
                "evidenceRole": str(file_manifest.get("evidenceRole") or "low_trust"),
                "sourceType": str(file_manifest.get("sourceType") or "misc"),
                "libraryRole": str(file_manifest.get("libraryRole") or "supplement_library"),
                "canJudge": "1" if file_manifest.get("canJudge") else "0",
                "canOverride": "1" if file_manifest.get("canOverride") else "0",
                "judgmentPolicy": judgment_policy,
                "school": school,
                "domains": ",".join(domains) if isinstance(domains, list) else str(domains),
                "topicScope": infer_topic_scope_hint(
                    chunk.text,
                    chunk.chapter,
                    topic_scope_list,
                ),
                "palaceScope": _scope_csv(palace_scope),
                "starScope": _scope_csv(star_scope),
                "mutagenScope": _scope_csv(mutagen_scope),
                "limitScope": _scope_csv(limit_scope),
                "textRole": text_role,
                "caseOnly": infer_case_only(text_role, judgment_policy),
            }
        )
        if len(ids) >= batch_size:
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
            ids, documents, metadatas = [], [], []

    if ids:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)


def build_category(
    client,
    embedding_fn,
    category_dir: Path,
    *,
    reset: bool,
) -> dict:
    folder_name = category_dir.name
    collection_id = folder_to_collection(folder_name)
    files = iter_source_files(category_dir)

    if reset:
        try:
            client.delete_collection(collection_id)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=collection_id,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine", "category": folder_name},
    )

    file_stats: list[dict] = []
    chunks_total = 0

    for path in files:
        rel = source_rel(path)
        try:
            suffix = path.suffix.lower()
            if suffix == ".txt":
                text = normalize_text(read_txt(path))
            elif suffix in (".docx", ".doc"):
                print(f"[read] {rel}", flush=True)
                text = read_document(path)
            else:
                raise ValueError(f"unsupported file type: {suffix}")

            if not text:
                file_stats.append({"file": rel, "status": "empty"})
                continue

            chunks = chunk_document(text, CHUNK_SIZE, CHUNK_OVERLAP)
            if not chunks:
                file_stats.append({"file": rel, "status": "empty"})
                continue

            book_meta = parse_filename(path.name)
            file_manifest = lookup_file_meta(path.name, rel)
            add_chunks(
                collection,
                rel=rel,
                file_name=path.name,
                category=folder_name,
                collection_id=collection_id,
                book_meta=book_meta,
                file_manifest=file_manifest,
                chunks=chunks,
            )
            chunks_total += len(chunks)
            file_stats.append({"file": rel, "status": "ok", "chars": len(text), "chunks": len(chunks)})
            print(f"[ok] {rel}: {len(chunks)} chunks", flush=True)
        except Exception as exc:
            file_stats.append({"file": rel, "status": f"error: {exc}"})
            print(f"[skip] {rel}: {exc}", flush=True)

    return {
        "category": folder_name,
        "collection": collection_id,
        "files_total": len(files),
        "chunks_total": chunks_total,
        "files": file_stats,
    }


def build_index(source_dir: Path, reset: bool = True, only_categories: list[str] | None = None) -> dict:
    category_dirs = list_category_dirs(source_dir)
    if only_categories:
        wanted = set(only_categories)
        category_dirs = [d for d in category_dirs if d.name in wanted or d.name[:2] in wanted]

    if not category_dirs:
        raise RuntimeError(f"no category folders found under {source_dir}")

    if reset and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=CHROMA_SETTINGS or Settings(anonymized_telemetry=False),
    )
    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL,
        device=resolve_device(),
    )

    categories_summary: list[dict] = []
    total_files = 0
    total_chunks = 0

    for category_dir in category_dirs:
        print(f"\n=== {category_dir.name} ===", flush=True)
        cat_reset = reset or bool(only_categories)
        cat_summary = build_category(client, embedding_fn, category_dir, reset=cat_reset)
        categories_summary.append(cat_summary)
        total_files += cat_summary["files_total"]
        total_chunks += cat_summary["chunks_total"]

    summary = {
        "status": "ready",
        "built_at": datetime.now().isoformat(timespec="seconds"),
        "source_dir": str(source_dir),
        "model": EMBED_MODEL,
        "files_total": total_files,
        "chunks_total": total_chunks,
        "categories": categories_summary,
    }
    report_path = DATA_DIR / "index_report.json"
    if only_categories and report_path.is_file():
        try:
            prior = json.loads(report_path.read_text(encoding="utf-8"))
            merged = {row.get("category"): row for row in prior.get("categories") or []}
            for row in categories_summary:
                merged[row.get("category")] = row
            categories_summary = list(merged.values())
            total_files = sum(int(row.get("files_total") or 0) for row in categories_summary)
            total_chunks = sum(int(row.get("chunks_total") or 0) for row in categories_summary)
            summary["categories"] = categories_summary
            summary["files_total"] = total_files
            summary["chunks_total"] = total_chunks
        except (json.JSONDecodeError, OSError):
            pass
    write_report(report_path, summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build multi-category knowledge base indexes")
    parser.add_argument("--source", default=str(SOURCE_DIR))
    parser.add_argument("--no-reset", action="store_true")
    parser.add_argument("--category", action="append", help="only build selected category folders")
    args = parser.parse_args()

    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"source dir not found: {source_dir}")
        return 1

    summary = build_index(source_dir, reset=not args.no_reset, only_categories=args.category)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
