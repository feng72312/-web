from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.core.knowledge.service import KnowledgeService
from app.core.knowledge.store import KnowledgeStore

_service: KnowledgeService | None = None


def default_knowledge_data_dir() -> Path:
    if settings.knowledge_data_dir:
        return Path(settings.knowledge_data_dir)
    backend_root = Path(__file__).resolve().parents[3]
    local = backend_root / "knowledge" / "data"
    if local.exists():
        return local
    return backend_root.parent / "knowledge" / "data"


def init_knowledge_service() -> KnowledgeService:
    global _service
    store = KnowledgeStore(default_knowledge_data_dir())
    if settings.knowledge_enabled:
        store.load()
    else:
        store.disable("disabled by config")
    _service = KnowledgeService(store)
    return _service


def get_knowledge_service() -> KnowledgeService:
    global _service
    if _service is None:
        return init_knowledge_service()
    return _service
