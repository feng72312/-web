from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.core.knowledge.case_store import CaseExperienceStore

KNOWLEDGE_DATA_DIR = Path(__file__).resolve().parents[4] / "knowledge" / "data"


@lru_cache(maxsize=1)
def get_case_store() -> CaseExperienceStore:
    store = CaseExperienceStore(KNOWLEDGE_DATA_DIR)
    store.load()
    return store
