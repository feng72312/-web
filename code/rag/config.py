from pathlib import Path
import os

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_ANONYMIZED_TELEMETRY", "False")

from categories import DEFAULT_CATEGORY, DEFAULT_COLLECTION

RAG_DIR = Path(__file__).resolve().parent
try:
    ROOT = RAG_DIR.parents[1]
except IndexError:
    ROOT = RAG_DIR
SOURCE_DIR = ROOT / "数据库"
DATA_DIR = RAG_DIR / "data"


def resolve_chroma_dir() -> Path:
    override = os.environ.get("RAG_CHROMA_DIR", "").strip()
    if override:
        return Path(override)
    for candidate in (Path("/mnt/chroma"), DATA_DIR / "chroma"):
        if (candidate / "chroma.sqlite3").exists():
            return candidate
    return DATA_DIR / "chroma"


CHROMA_DIR = resolve_chroma_dir()

EMBED_MODEL = "BAAI/bge-small-zh-v1.5"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
RERANK_ENABLED = os.environ.get("RAG_RERANK", "0").strip().lower() in {"1", "true", "yes", "on"}
RERANK_MODEL = os.environ.get("RAG_RERANK_MODEL", "BAAI/bge-reranker-base")
RAG_DEVICE = os.environ.get("RAG_DEVICE", "auto")


def resolve_device() -> str:
    raw = (RAG_DEVICE or "auto").strip().lower() or "auto"
    if raw == "cpu":
        return "cpu"
    if raw == "cuda":
        return "cuda"
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


try:
    from chromadb.config import Settings as ChromaSettings

    CHROMA_SETTINGS = ChromaSettings(anonymized_telemetry=False)
except Exception:  # pragma: no cover
    CHROMA_SETTINGS = None

HOST = os.environ.get("RAG_HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8100"))

ALLOWED_SUFFIXES = {".txt", ".doc", ".docx"}

DEFAULT_RAG_CATEGORY = DEFAULT_CATEGORY
DEFAULT_RAG_COLLECTION = DEFAULT_COLLECTION

# backward compat
COLLECTION_NAME = DEFAULT_COLLECTION
