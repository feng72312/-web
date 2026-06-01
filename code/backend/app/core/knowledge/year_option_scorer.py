"""Deterministic scores for year-as-option MCQ (hint block only)."""

from __future__ import annotations

import re
from typing import Any

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.option_exclusion import _option_letter_and_text, _year_signals
from app.core.knowledge.target_year_block import _resolve_year_luck

_YEAR_OPT = re.compile(r"(19|20)\d{2}")


def parse_year_from_option(opt: str) -> int | None:
    m = _YEAR_OPT.search(opt or "")
    if not m:
        return None
    return int(m.group(0))


def score_year_option(
    chart: dict[str, Any],
    question: str,
    year: int,
) -> float:
    theme = infer_question_theme(question)
    dy, ln = _resolve_year_luck(chart, year)
    sig = _year_signals(chart, dy, ln)
    if not sig:
        return 0.25
    score = 0.35
    if theme in ("流年事件", "官非"):
        if sig.get("has_guansha"):
            score += 0.25
        if sig.get("heavy_clash"):
            score += 0.2
        if sig.get("has_jiebi"):
            score += 0.1
    elif theme == "健康疾病":
        if sig.get("heavy_clash") and (
            sig.get("has_yin") or sig.get("has_guansha")
        ):
            score += 0.35
        elif sig.get("has_cai") and sig.get("heavy_clash"):
            score += 0.15
    elif theme == "婚姻感情":
        if sig.get("has_cai") or sig.get("has_guansha"):
            score += 0.25
        if sig.get("heavy_clash"):
            score += 0.1
    elif theme == "职业财运":
        if sig.get("has_cai"):
            score += 0.25
    else:
        if sig.get("has_cai") or sig.get("has_guansha") or sig.get("heavy_clash"):
            score += 0.15
    return min(score, 1.0)


def build_year_option_score_block(
    chart: dict[str, Any],
    question: str,
    options: list[str],
) -> str:
    rows: list[str] = []
    for opt in options:
        letter, _text = _option_letter_and_text(opt)
        year = parse_year_from_option(opt)
        if year is None:
            continue
        sc = score_year_option(chart, question, year)
        rows.append(f"{letter} {year}年 规则分{sc:.2f}")
    if not rows:
        return ""
    return (
        "【年份选项规则分】(仅供参考, 须结合题干与选项全文, 勿单凭分数作答):\n"
        + "\n".join(rows)
    )
