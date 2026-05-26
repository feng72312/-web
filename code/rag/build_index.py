"""Build local semantic index from txt/doc files under 数据库/八字."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from chunker import chunk_text
from config import (
    ALLOWED_SUFFIXES,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DATA_DIR,
    EMBED_MODEL,
    SOURCE_DIR,
)
from doc_reader import read_document, read_doc_batch, read_txt, read_docx, normalize_text


def iter_source_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            continue
        if "ocr" in path.parts:
            continue
        files.append(path)
    return files


def build_index(source_dir: Path, reset: bool = True) -> dict:
    files = iter_source_files(source_dir)
    if not files:
        raise RuntimeError(f"no txt/doc files found under {source_dir}")

    if reset and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str | int]] = []

    file_stats: list[dict] = []
    doc_paths = [path for path in files if path.suffix.lower() == ".doc"]
    doc_texts: dict[Path, str] = {}
    if doc_paths:
        try:
            raw_docs = read_doc_batch(doc_paths)
            for path, raw in raw_docs.items():
                text = normalize_text(raw)
                if text:
                    doc_texts[path] = text
        except Exception as exc:
            print(f"[warn] batch doc read failed, fallback to single-file mode: {exc}")
            for path in doc_paths:
                try:
                    doc_texts[path] = read_document(path)
                except Exception as single_exc:
                    print(f"[skip] {path.name}: {single_exc}")

    for path in files:
        rel = str(path.relative_to(source_dir))
        try:
            suffix = path.suffix.lower()
            if suffix == ".txt":
                text = normalize_text(read_txt(path))
            elif suffix == ".docx":
                text = normalize_text(read_docx(path))
            elif suffix == ".doc":
                text = doc_texts.get(path, "")
                if not text:
                    raise ValueError(f"empty or unreadable doc: {path.name}")
            else:
                raise ValueError(f"unsupported file type: {suffix}")

            if not text:
                file_stats.append({"file": rel, "status": "empty"})
                continue

            chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
            if not chunks:
                file_stats.append({"file": rel, "status": "empty"})
                continue

            for index, chunk in enumerate(chunks):
                ids.append(str(uuid.uuid4()))
                documents.append(chunk)
                metadatas.append(
                    {
                        "source": rel,
                        "chunk_index": index,
                        "file_name": path.name,
                    }
                )

            file_stats.append(
                {
                    "file": rel,
                    "status": "ok",
                    "chars": len(text),
                    "chunks": len(chunks),
                }
            )
            print(f"[ok] {rel}: {len(chunks)} chunks")
        except Exception as exc:
            file_stats.append({"file": rel, "status": f"error: {exc}"})
            print(f"[skip] {rel}: {exc}")

    if not documents:
        raise RuntimeError("no chunks indexed, check source files and doc reader")

    batch_size = 64
    for start in range(0, len(documents), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    summary = {
        "status": "ready",
        "built_at": datetime.now().isoformat(timespec="seconds"),
        "source_dir": str(source_dir),
        "model": EMBED_MODEL,
        "files_total": len(files),
        "chunks_total": len(documents),
        "files": file_stats,
    }

    report_path = DATA_DIR / "index_report.json"
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build bazi local knowledge base index")
    parser.add_argument(
        "--source",
        default=str(SOURCE_DIR),
        help="source directory containing txt/doc files",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="append to existing index instead of rebuilding",
    )
    args = parser.parse_args()

    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"source dir not found: {source_dir}")
        return 1

    summary = build_index(source_dir, reset=not args.no_reset)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
