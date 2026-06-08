from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


@lru_cache(maxsize=1)
def _load_entries() -> list[dict[str, str]]:
    path = DATA_DIR / "jiemeng_entries.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("entries", [])


def _normalize_query(text: str) -> str:
    text = re.sub(r"\s+", "", text.strip())
    text = re.sub(r"^(梦见|梦到|做梦|梦见|夜里梦|昨晚梦|曾经梦)", "", text)
    return text


def _tokens(text: str) -> list[tuple[str, int]]:
    text = _normalize_query(text)
    chunks: list[tuple[str, int]] = []
    seen: set[str] = set()

    def add(chunk: str, weight: int) -> None:
        if chunk and chunk not in seen:
            seen.add(chunk)
            chunks.append((chunk, weight))

    for size in (4, 3, 2):
        for i in range(len(text) - size + 1):
            add(text[i : i + size], size)
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff" and ch not in "见梦到的":
            add(ch, 1)
    return chunks


def search_dreams(query: str, *, limit: int = 8) -> list[dict[str, str]]:
    raw = re.sub(r"\s+", "", query.strip())
    q = _normalize_query(raw)
    if len(q) < 2:
        raise ValueError("dream query too short")

    tokens = _tokens(raw)
    scored: list[tuple[int, dict[str, str]]] = []
    for entry in _load_entries():
        text = entry.get("text", "")
        section = entry.get("section", "")
        haystack = f"{section}{text}"
        score = 0
        for token, weight in tokens:
            if token in haystack:
                score += weight
        if q in haystack:
            score += len(q) + 4
        if score <= 0:
            continue
        scored.append((score, entry))

    scored.sort(key=lambda item: (-item[0], item[1].get("text", "")))
    results: list[dict[str, str]] = []
    for score, entry in scored[:limit]:
        results.append(
            {
                "section": entry.get("section", ""),
                "text": entry.get("text", ""),
                "score": str(score),
            }
        )
    return results
