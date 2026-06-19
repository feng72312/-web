"""Deterministic scores for year-as-option MCQ (hint block only)."""

from __future__ import annotations

import re
from typing import Any

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.option_exclusion import _option_letter_and_text, _year_signals
from app.core.knowledge.target_year_block import _resolve_year_luck

_YEAR_OPT = re.compile(r"(19|20)\d{2}")


def parse_year_from_option(opt: str) -> int | None:
    years = parse_years_from_option(opt)
    return years[0] if years else None


def parse_years_from_option(opt: str) -> list[int]:
    found: list[int] = []
    for m in _YEAR_OPT.finditer(opt or ""):
        y = int(m.group(0))
        if 1900 <= y <= 2100:
            found.append(y)
    return sorted(set(found))


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
    elif theme == "学历":
        if sig.get("has_yin"):
            score += 0.2
        if sig.get("has_shishang"):
            score += 0.1
        if sig.get("heavy_clash"):
            score += 0.05
    elif theme == "家庭出身":
        q = question or ""
        if "父亲" in q or ("父" in q and "父母" not in q):
            if sig.get("has_cai"):
                score += 0.25
            if sig.get("heavy_clash"):
                score += 0.25
            if sig.get("has_guansha"):
                score += 0.1
        elif "母亲" in q or ("母" in q and "父母" not in q):
            if sig.get("has_yin"):
                score += 0.25
            if sig.get("heavy_clash"):
                score += 0.25
        else:
            if sig.get("has_cai"):
                score += 0.15
            if sig.get("has_yin"):
                score += 0.15
            if sig.get("heavy_clash"):
                score += 0.15
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
        years = parse_years_from_option(opt)
        if not years:
            continue
        scores = [score_year_option(chart, question, year) for year in years]
        sc = sum(scores) / len(scores)
        year_label = ",".join(str(y) for y in years)
        rows.append(f"{letter} {year_label}年 规则分{sc:.2f}")
    if not rows:
        return ""
    q = question or ""
    if "父亲" in q or ("父" in q and "父母" not in q):
        hint = "丧父题重偏财冲合克; 冲根/合去之年不得仅因规则分低排除"
    elif "母亲" in q or ("母" in q and "父母" not in q):
        hint = "丧母题重印星受克; 生扶合化助印之年通常非丧母"
    else:
        hint = "须与各选项年份及父母星互证"
    return (
        f"【选项年份岁运评分】({hint}, 优先候选规则分较高且引动明确项):\n"
        + "\n".join(rows)
    )
