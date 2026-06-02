from pathlib import Path
import os

from categories import DEFAULT_CATEGORY, DEFAULT_COLLECTION

RAG_DIR = Path(__file__).resolve().parent
try:
    ROOT = RAG_DIR.parents[1]
except IndexError:
    ROOT = RAG_DIR
SOURCE_DIR = ROOT / "数据库"
DATA_DIR = RAG_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"

EMBED_MODEL = "BAAI/bge-small-zh-v1.5"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

HOST = os.environ.get("RAG_HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8100"))

ALLOWED_SUFFIXES = {".txt", ".doc", ".docx"}

DEFAULT_RAG_CATEGORY = DEFAULT_CATEGORY
DEFAULT_RAG_COLLECTION = DEFAULT_COLLECTION

# backward compat
COLLECTION_NAME = DEFAULT_COLLECTION
