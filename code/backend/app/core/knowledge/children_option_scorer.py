"""Deterministic children MCQ option scores (birth-year hint block)."""

from __future__ import annotations

import re
from typing import Any

from app.core.knowledge.children_subtheme import ChildrenSubtheme, infer_children_subtheme
from app.core.knowledge.option_exclusion import _option_letter_and_text
from app.core.knowledge.shishen_context import _chart_gender
from app.core.knowledge.target_year_block import _resolve_year_luck
from app.core.knowledge.year_option_scorer import parse_years_from_option
from app.core.paipan.interactions import ZHI_CHONG, ZHI_HE

_GUAN = frozenset({"正官", "七杀"})
_SHI = frozenset({"食神", "伤官"})
_YIN = frozenset({"正印", "偏印"})
_SANHE_HALF: frozenset[tuple[str, str]] = frozenset(
    {
        ("寅", "午"),
        ("午", "戌"),
        ("亥", "卯"),
        ("卯", "未"),
        ("巳", "酉"),
        ("酉", "丑"),
        ("申", "子"),
        ("子", "辰"),
    }
)


def _sanhe_half(day_zhi: str, ln_zhi: str) -> bool:
    if not day_zhi or not ln_zhi:
        return False
    pair = (day_zhi, ln_zhi)
    return pair in _SANHE_HALF or (pair[1], pair[0]) in _SANHE_HALF


def _childbearing_age_bonus(chart: dict[str, Any], year: int) -> float:
    birth_year = int(chart.get("birthYear") or 0)
    if birth_year <= 0:
        return 0.0
    age = year - birth_year + 1
    if 24 <= age <= 36:
        return 0.10
    if 37 <= age <= 42:
        return 0.04
    return -0.04


def _hide_has(ss_set: frozenset[str], hide_stems: list[str]) -> bool:
    for item in hide_stems or []:
        m = re.search(r"\(([^)]+)\)", item)
        if m and m.group(1).strip() in ss_set:
            return True
    return False


def _branch_clash(a: str, b: str) -> bool:
    if not a or not b:
        return False
    for x, y in ZHI_CHONG:
        if (a, b) in ((x, y), (y, x)):
            return True
    return False


def _hour_branch_relation(chart: dict[str, Any], ln_zhi: str) -> str:
    hour_zhi = str((chart.get("pillars") or {}).get("hour", {}).get("zhi") or "")
    if not hour_zhi or not ln_zhi:
        return ""
    for x, y in ZHI_CHONG:
        if (hour_zhi, ln_zhi) in ((x, y), (y, x)):
            return "chong"
    for x, y in ZHI_HE:
        if (hour_zhi, ln_zhi) in ((x, y), (y, x)):
            return "he"
    return ""


def score_children_birth_year(
    chart: dict[str, Any],
    year: int,
    *,
    is_female: bool,
) -> float:
    dy, ln = _resolve_year_luck(chart, year)
    if not ln:
        return 0.15
    lp = ln.get("pillar") or {}
    dp = (dy or {}).get("pillar") or {}
    hide = lp.get("hideStems") or []
    stem = (lp.get("shishenGan") or "").strip()
    dy_stem = (dp.get("shishenGan") or "").strip()
    child_star = _SHI if is_female else _GUAN
    hr = _hour_branch_relation(chart, lp.get("zhi") or "")

    score = 0.18

    if stem in child_star:
        score += 0.40
    elif _hide_has(child_star, hide):
        score += 0.12

    if dy_stem in child_star:
        score += 0.06

    if hr == "he":
        score += 0.10
    elif hr == "chong":
        if is_female and stem in _SHI:
            score -= 0.12
        elif is_female and stem in _GUAN and _hide_has(_SHI, hide):
            score += 0.08
        elif not is_female and stem in _YIN and not _hide_has(_GUAN, hide):
            score -= 0.14
        elif not is_female and _hide_has(_GUAN, hide):
            score += 0.06
        else:
            score += 0.04

    if is_female:
        if stem in _GUAN and _hide_has(_SHI, hide):
            score += 0.14
        if stem in _GUAN and not _hide_has(_SHI, hide):
            score -= 0.08
    else:
        if stem in _YIN and _hide_has(_GUAN, hide):
            score += 0.08
        elif stem in _YIN and _hide_has(_SHI, hide) and not _hide_has(_GUAN, hide):
            score -= 0.06
        if stem in _SHI and not _hide_has(_GUAN, hide):
            score -= 0.10

    if stem in _YIN and not _hide_has(child_star, hide) and hr != "he":
        score -= 0.05

    day_zhi = str((chart.get("pillars") or {}).get("day", {}).get("zhi") or "")
    ln_zhi = lp.get("zhi") or ""
    if _sanhe_half(day_zhi, ln_zhi):
        score += 0.16
    if _branch_clash(day_zhi, ln_zhi):
        score -= 0.12
    if dy and ln.get("ganzhi") and dy.get("ganzhi") == ln.get("ganzhi"):
        score -= 0.12

    if not is_female and stem in _GUAN and _hide_has(_SHI, hide):
        score -= 0.10

    dy_stem_ss = dy_stem
    if not is_female and dy_stem_ss in _YIN and stem in _GUAN:
        score -= 0.16

    score += _childbearing_age_bonus(chart, year)

    return min(max(score, 0.05), 1.0)


def _prefers_recent_child_year(question: str) -> bool:
    q = question or ""
    return any(k in q for k in ("目前", "现有", "现在", "现已"))


def score_children_option(
    chart: dict[str, Any],
    question: str,
    option: str,
    subtheme: ChildrenSubtheme | None = None,
    *,
    option_years_max: int | None = None,
) -> float:
    st = subtheme or infer_children_subtheme(question, [option])
    if st != "children-birth-year":
        return 0.25
    years = parse_years_from_option(option)
    if not years:
        return 0.25
    is_female = _chart_gender(chart) == "female"
    scores = [score_children_birth_year(chart, y, is_female=is_female) for y in years]
    base = sum(scores) / len(scores)
    if (
        _prefers_recent_child_year(question)
        and option_years_max is not None
        and max(years) == option_years_max
    ):
        base += 0.22
    return min(base, 1.0)


def build_children_option_score_block(
    chart: dict[str, Any],
    question: str,
    options: list[str],
    subtheme: ChildrenSubtheme | None = None,
) -> str:
    st = subtheme or infer_children_subtheme(question, options)
    if st != "children-birth-year":
        return ""
    gender = _chart_gender(chart)
    star = "食伤" if gender == "female" else "官杀"
    all_years = [
        y for opt in options for y in parse_years_from_option(opt)
    ]
    option_years_max = max(all_years) if all_years else None
    rows: list[str] = []
    for opt in options:
        letter, _text = _option_letter_and_text(opt)
        years = parse_years_from_option(opt)
        if not years:
            continue
        sc = score_children_option(
            chart,
            question,
            opt,
            subtheme=st,
            option_years_max=option_years_max,
        )
        year_label = ",".join(str(y) for y in years)
        rows.append(f"{letter} {year_label}年 规则分{sc:.2f}")
    if not rows:
        return ""
    recent_note = (
        "题干问「目前/现有」孩子时, 须结合命盘引动与选项年份, 勿仅选最早年; "
        if _prefers_recent_child_year(question)
        else ""
    )
    hint = (
        f"女命看食伤、男命看官杀为子女星; 仅时支冲/合子女宫加分; "
        f"藏干须与流年天干互证; {recent_note}"
        f"本题以{star}为主; 规则分仅供与排盘互证, 分差<0.08时不得单凭分数作答"
    )
    return f"【子女选项规则分】({hint}):\n" + "\n".join(rows)
