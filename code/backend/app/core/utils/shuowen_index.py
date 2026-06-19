from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.core.utils.data_paths import utils_data_dir

DATA_DIR = utils_data_dir()


@lru_cache(maxsize=1)
def _load_entries() -> dict[str, dict]:
    path = DATA_DIR / "shuowen_entries.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("entries", {})


def lookup_char(char: str) -> dict | None:
    char = char.strip()
    if not char or len(char) != 1:
        return None
    entry = _load_entries().get(char)
    if not entry:
        return None
    return dict(entry)


def lookup_chars(text: str) -> list[dict]:
    results: list[dict] = []
    seen: set[str] = set()
    for ch in text:
        if not ("\u4e00" <= ch <= "\u9fff"):
            continue
        if ch in seen:
            continue
        seen.add(ch)
        entry = lookup_char(ch)
        if entry:
            results.append(entry)
        else:
            results.append({"char": ch, "explanation": "", "radical": "", "missing": True})
    return results
