from __future__ import annotations

import json
from pathlib import Path

from app.config import settings

_CASES: list[dict] | None = None
_LOAD_ERROR = ""


def _cases_path() -> Path:
    base = Path(settings.knowledge_data_dir) if settings.knowledge_data_dir else Path(__file__).resolve().parents[3] / "knowledge" / "data"
    gold = base / "cases" / "xingming_cases_gold.jsonl"
    if settings.xingming_case_gold_only and gold.exists():
        return gold
    return base / "cases" / "xingming_cases.jsonl"


def load_cases() -> list[dict]:
    global _CASES, _LOAD_ERROR
    if _CASES is not None:
        return _CASES
    path = _cases_path()
    if not path.exists():
        _CASES = []
        _LOAD_ERROR = f"cases file not found: {path}"
        return _CASES
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    _CASES = rows
    return rows


def _score_case(case: dict, palace: str, star_ids: set[str], question: str) -> int:
    score = 0
    cond = case.get("conditions") or {}
    if cond.get("palace") and cond["palace"] == palace:
        score += 3
    case_stars = set(cond.get("starIds") or [])
    if case_stars & star_ids:
        score += 2 * len(case_stars & star_ids)
    qtype = (case.get("questionType") or "").strip()
    if qtype and qtype in question:
        score += 2
    if case.get("tier") == "gold":
        score += 1
    return score


def search_cases(
    chart: dict,
    question: str,
    *,
    tier: str | None = "gold",
    top_k: int = 5,
) -> list[dict]:
    cases = load_cases()
    ming = chart.get("mingPalace") or {}
    palace = ming.get("branch") or (chart.get("palaces") or [{}])[0].get("branch", "")
    star_ids = {s.get("id") for s in ming.get("majorStars") or [] if s.get("id")}
    for s in ming.get("minorStars") or []:
        if s.get("id"):
            star_ids.add(s["id"])
    ranked: list[tuple[int, dict]] = []
    for case in cases:
        if tier and case.get("tier") != tier:
            continue
        sc = _score_case(case, palace, star_ids, question)
        if sc > 0:
            ranked.append((sc, case))
    ranked.sort(key=lambda x: (-x[0], x[1].get("id", "")))
    return [c for _, c in ranked[:top_k]]
