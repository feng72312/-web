from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
MODULUS = 384


def reduce_stroke(count: int) -> int:
    while count > 9:
        if count in (10, 20):
            return 0
        count -= 10
    return count


def compute_qian_number(hundreds: int, tens: int, ones: int) -> tuple[int, list[str]]:
    total = hundreds * 100 + tens * 10 + ones
    steps: list[str] = [
        f"百位 {hundreds}, 十位 {tens}, 个位 {ones}, 合计 {total}",
    ]
    while total > MODULUS:
        total -= MODULUS
        steps.append(f"减去 {MODULUS}, 余 {total}")
    steps.append(f"签号 {total}")
    return total, steps


@lru_cache(maxsize=1)
def _load_qian() -> dict[str, str]:
    path = DATA_DIR / "zhuge_qian.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("qian", {})


@lru_cache(maxsize=1)
def _load_strokes() -> dict[str, int]:
    path = DATA_DIR / "zhuge_strokes.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def stroke_count(char: str, overrides: dict[str, int] | None = None) -> int:
    if len(char) != 1:
        raise ValueError("stroke_count expects one character")
    table = _load_strokes()
    if overrides and char in overrides:
        return overrides[char]
    if char in table:
        return table[char]
    raise ValueError(f"unknown stroke for character: {char}")


def divine_three_chars(
    chars: str,
    *,
    strokes: list[int] | None = None,
) -> dict:
    normalized = re.sub(r"\s+", "", chars)
    if len(normalized) != 3:
        raise ValueError("zhuge requires exactly three characters")

    raw_strokes: list[int] = []
    reduced: list[int] = []
    if strokes is not None:
        if len(strokes) != 3:
            raise ValueError("strokes must have length 3")
        raw_strokes = [int(s) for s in strokes]
        reduced = [reduce_stroke(s) for s in raw_strokes]
    else:
        for ch in normalized:
            count = stroke_count(ch)
            raw_strokes.append(count)
            reduced.append(reduce_stroke(count))

    qian_no, steps = compute_qian_number(reduced[0], reduced[1], reduced[2])
    qian = _load_qian()
    text = qian.get(str(qian_no), "")
    missing = not text

    return {
        "chars": normalized,
        "rawStrokes": raw_strokes,
        "reducedStrokes": reduced,
        "qianNo": qian_no,
        "qianText": text or f"签号 {qian_no} 签文尚未收录 (典籍仅含部分签条).",
        "steps": steps,
        "missingText": missing,
    }
