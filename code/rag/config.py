from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "数据库" / "八字"
DATA_DIR = Path(__file__).resolve().parent / "data"
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION_NAME = "bazi_classics"

EMBED_MODEL = "BAAI/bge-small-zh-v1.5"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

HOST = "127.0.0.1"
PORT = 8100

ALLOWED_SUFFIXES = {".txt", ".doc", ".docx"}
