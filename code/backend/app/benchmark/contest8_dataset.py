from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

SplitName = Literal["train", "val", "test"]

SPLIT_YEARS: dict[SplitName, tuple[int, ...]] = {
    "train": (2021, 2022, 2023),
    "val": (2024,),
    "test": (2025,),
}

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[4] / "命理师大赛试题" / "data"


@dataclass(frozen=True)
class ContestQuestion:
    year: int
    person_id: str
    question_id: str
    question: str
    options: list[str]
    answer: str
    birth: dict[str, Any]
    gender: str
    person_name: str
    extra_info: dict[str, Any]


def contest_data_dir(base: Path | None = None) -> Path:
    if base is not None:
        return base
    return DEFAULT_DATA_DIR


def load_year_file(year: int, data_dir: Path | None = None) -> list[dict[str, Any]]:
    path = contest_data_dir(data_dir) / f"contest8_{year}.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing contest data: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [row for row in raw if row.get("person_id")]


def normalize_answer_letter(text: str) -> str:
    m = re.search(r"[ABCDabcd]", text.strip())
    if not m:
        return ""
    return m.group(0).upper()


_FIT_LINE = re.compile(
    r"^([ABCDabcd])\s*[:：]\s*符合\b",
    re.IGNORECASE | re.MULTILINE,
)


def extract_single_fit_letter_from_reasoning(text: str) -> str:
    """Return letter if exactly one option is marked 符合 in the exclusion block."""
    body = text or ""
    start = body.find("【选项排除】")
    if start < 0:
        start = body.find("选项排除")
    segment = body[start:] if start >= 0 else body
    end = segment.find("【结论】")
    if end > 0:
        segment = segment[:end]
    fits = [m.group(1).upper() for m in _FIT_LINE.finditer(segment)]
    if len(fits) == 1:
        return fits[0]
    return ""


def _letter_from_final_line(body: str) -> str:
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    for ln in reversed(lines):
        m = re.match(r"^答案\s*[:：]\s*([ABCDabcd])\s*\.?$", ln, flags=re.IGNORECASE)
        if m:
            return m.group(1).upper()
        m = re.match(r"^最终答案\s*[:：]\s*([ABCDabcd])\s*\.?$", ln, flags=re.IGNORECASE)
        if m:
            return m.group(1).upper()
        if re.fullmatch(r"[ABCDabcd]", ln):
            return ln.upper()
    found = re.findall(r"[ABCDabcd]", body)
    if found:
        return found[-1].upper()
    return ""


def parse_contest_answer_letter(
    text: str,
    *,
    prefer_final_line: bool = False,
    reconcile_reasoning: bool = False,
) -> tuple[str, str]:
    """
    Parse MCQ letter.
    Returns (letter, parse_source) where parse_source is
    final_line | reasoning_fit | fallback | empty.
    """
    body = (text or "").strip()
    if not body:
        return "", "empty"
    if not prefer_final_line:
        letter = normalize_answer_letter(body)
        return letter, ("fallback" if letter else "empty")
    line_letter = _letter_from_final_line(body)
    if reconcile_reasoning:
        fit_letter = extract_single_fit_letter_from_reasoning(body)
        if fit_letter and line_letter and fit_letter != line_letter:
            return fit_letter, "reasoning_fit"
        if fit_letter and not line_letter:
            return fit_letter, "reasoning_fit"
        if line_letter:
            return line_letter, "final_line"
        if fit_letter:
            return fit_letter, "reasoning_fit"
        return "", "empty"
    if line_letter:
        return line_letter, "final_line"
    return "", "empty"


def flatten_questions(
    years: tuple[int, ...] | list[int],
    data_dir: Path | None = None,
) -> list[ContestQuestion]:
    items: list[ContestQuestion] = []
    for year in years:
        for person in load_year_file(year, data_dir):
            profile = person.get("profile") or {}
            birth = profile.get("birth") or {}
            gender = str(profile.get("gender") or "male")
            extra = profile.get("extra_info") or {}
            for q in person.get("questions") or []:
                items.append(
                    ContestQuestion(
                        year=year,
                        person_id=str(person.get("person_id", "")),
                        question_id=str(q.get("question_id", "")),
                        question=str(q.get("question", "")),
                        options=[str(o) for o in q.get("options") or []],
                        answer=normalize_answer_letter(str(q.get("answer", ""))),
                        birth=birth,
                        gender=gender,
                        person_name=str(person.get("name", "")),
                        extra_info=extra if isinstance(extra, dict) else {},
                    )
                )
    return items


def load_split(split: SplitName, data_dir: Path | None = None) -> list[ContestQuestion]:
    return flatten_questions(SPLIT_YEARS[split], data_dir)


def split_summary(data_dir: Path | None = None) -> dict[str, int]:
    return {name: len(load_split(name, data_dir)) for name in SPLIT_YEARS}
