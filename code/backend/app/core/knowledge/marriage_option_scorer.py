"""Deterministic marriage MCQ option scores (hint block only)."""

from __future__ import annotations

import re
from typing import Any

from app.core.knowledge.marriage_subtheme import MarriageSubtheme, infer_marriage_subtheme
from app.core.knowledge.option_exclusion import (
    _option_letter_and_text,
    _year_signals,
)
from app.core.knowledge.shishen_context import _chart_gender
from app.core.knowledge.target_year_block import _resolve_year_luck
from app.core.knowledge.year_option_scorer import parse_years_from_option
from app.core.paipan.interactions import ZHI_CHONG, ZHI_HE

_CAI = frozenset({"正财", "偏财"})
_GUAN = frozenset({"正官", "七杀"})
_SHI = frozenset({"食神", "伤官"})
_JIE = frozenset({"比肩", "劫财"})

_DIVORCE_Q = ("离婚", "分居", "拆伙", "分开")
_MARRY_Q = ("结婚", "成婚", "嫁", "娶", "联姻", "冲喜", "第二婚", "再婚", "再嫁")
_AFFAIR_Q = ("外遇", "桃花", "私情", "同性恋", "同居", "情人")
_SINGLE_OPT = ("单身", "未婚", "从未结婚", "光棍", "无婚", "独身")
_TIMING_Q_KEYS = (
    "哪年",
    "哪一年",
    "何时",
    "什么时候",
    "于哪",
)

RULE_SCORE_MARGIN_STRONG = 0.25
RULE_SCORE_TOP_MIN = 0.55


def _hide_has(ss_set: frozenset[str], hide_stems: list[str]) -> bool:
    for item in hide_stems or []:
        m = re.search(r"\(([^)]+)\)", item)
        if m and m.group(1).strip() in ss_set:
            return True
    return False


def _branch_relation(a: str, b: str) -> str:
    if not a or not b:
        return ""
    for x, y in ZHI_CHONG:
        if (a, b) in ((x, y), (y, x)):
            return "chong"
    for x, y in ZHI_HE:
        if (a, b) in ((x, y), (y, x)):
            return "he"
    return ""


def _event_kind(question: str) -> str:
    q = question or ""
    if any(k in q for k in ("第二婚", "再婚", "再嫁")):
        return "marry"
    if any(k in q for k in _DIVORCE_Q) and not any(
        k in q for k in ("第二婚", "再婚", "再嫁")
    ):
        return "divorce"
    if any(k in q for k in _AFFAIR_Q):
        return "affair"
    if any(k in q for k in _MARRY_Q):
        return "marry"
    return "neutral"


def _spouse_sets(is_female: bool) -> frozenset[str]:
    return _GUAN if is_female else _CAI


def _is_year_only_option(text: str) -> bool:
    t = (text or "").strip()
    years = parse_years_from_option(t)
    if not years:
        return False
    rest = t
    for y in years:
        rest = rest.replace(str(y), "").replace("年", "")
    return len(rest.strip()) <= 2


def _marriage_age_bonus(chart: dict[str, Any], year: int, *, event: str) -> float:
    birth_year = int(chart.get("birthYear") or 0)
    if birth_year <= 0:
        return 0.0
    age = year - birth_year + 1
    if event == "marry":
        if 24 <= age <= 40:
            return 0.10
        if 41 <= age <= 52:
            return 0.04
        if age < 20:
            return -0.14
    if 22 <= age <= 38:
        return 0.06
    if age < 18:
        return -0.12
    return -0.02


def score_marriage_year(
    chart: dict[str, Any],
    question: str,
    year: int,
    *,
    is_female: bool | None = None,
) -> float:
    if is_female is None:
        is_female = _chart_gender(chart) == "female"
    spouse = _spouse_sets(is_female)
    event = _event_kind(question)

    dy, ln = _resolve_year_luck(chart, year)
    if not ln:
        if dy:
            dp = dy.get("pillar") or {}
            dy_stem = (dp.get("shishenGan") or "").strip()
            score = 0.22
            if dy_stem in spouse:
                score += 0.12
            score += _marriage_age_bonus(chart, year, event=event)
            return min(max(score, 0.08), 0.45)
        return 0.12

    sig = _year_signals(chart, dy, ln)
    if not sig:
        return 0.12

    lp = ln.get("pillar") or {}
    dp = (dy or {}).get("pillar") or {}
    stem = (lp.get("shishenGan") or "").strip()
    dy_stem = (dp.get("shishenGan") or "").strip()
    hide = lp.get("hideStems") or []
    day_zhi = str((chart.get("pillars") or {}).get("day", {}).get("zhi") or "")
    ln_zhi = lp.get("zhi") or ""
    day_rel = _branch_relation(day_zhi, ln_zhi)

    score = 0.18

    if stem in spouse:
        score += 0.36
    elif _hide_has(spouse, hide):
        score += 0.16

    if dy_stem in spouse:
        score += 0.08

    if event == "marry":
        if stem in spouse or _hide_has(spouse, hide):
            score += 0.10
        if day_rel == "he":
            score += 0.14
        elif day_rel == "chong":
            score += 0.05
        if stem in _JIE and not is_female:
            score -= 0.12
        if stem in _SHI and is_female:
            score -= 0.10
    elif event == "divorce":
        if day_rel == "chong" or sig.get("day_clash"):
            score += 0.22
        if stem in _JIE and not is_female:
            score += 0.10
        if stem in _SHI and is_female:
            score += 0.12
        if day_rel == "he" and (stem in spouse or _hide_has(spouse, hide)):
            score -= 0.12
    elif event == "affair":
        if stem in _CAI or stem in _SHI:
            score += 0.14
        if day_rel == "chong":
            score += 0.08
    else:
        if stem in spouse or _hide_has(spouse, hide):
            score += 0.10
        if day_rel == "he":
            score += 0.10
        elif day_rel == "chong":
            score += 0.06

    if not is_female and stem in _JIE and (stem in _CAI or _hide_has(_CAI, hide)):
        score -= 0.10
    if is_female and stem in _SHI and (stem in _GUAN or _hide_has(_GUAN, hide)):
        score -= 0.10

    score += _marriage_age_bonus(chart, year, event=event)
    return min(max(score, 0.05), 1.0)


def score_marriage_single_option(
    chart: dict[str, Any],
    question: str,
    option_text: str,
) -> float:
    is_female = _chart_gender(chart) == "female"
    profile = _chart_marriage_profile(chart, is_female)
    q = question or ""
    asks_marry = any(k in q for k in _MARRY_Q + _TIMING_Q_KEYS)
    table = {
        "weak_spouse": 0.68,
        "rival_heavy": 0.52,
        "spouse_active": 0.22,
        "neutral": 0.42,
    }
    base = table.get(profile, 0.40)
    if asks_marry and profile in ("spouse_active", "neutral"):
        base -= 0.18
    if any(k in q for k in _DIVORCE_Q):
        base += 0.08
    return min(max(base, 0.05), 0.85)


def _narrative_tags(text: str) -> set[str]:
    t = text or ""
    tags: set[str] = set()
    if any(k in t for k in ("离婚", "分居", "拆伙", "独身")):
        tags.add("divorce")
    if any(k in t for k in _SINGLE_OPT):
        tags.add("single")
    if any(k in t for k in ("外遇", "私情", "同性恋", "同居", "情人", "劈腿")):
        tags.add("affair")
    if any(k in t for k in ("结婚", "成婚", "美满", "再婚", "嫁", "娶")):
        tags.add("married")
    if any(k in t for k in ("恋爱", "拍拖", "男友", "女友")):
        tags.add("dating")
    return tags


def _chart_marriage_profile(chart: dict[str, Any], is_female: bool) -> str:
    spouse = _spouse_sets(is_female)
    cai = guan = bi = 0
    spouse_root = False
    for pillar in (chart.get("pillars") or {}).values():
        ss = (pillar.get("shishenGan") or "").strip()
        if ss in _CAI:
            cai += 1
        if ss in _GUAN:
            guan += 1
        if ss in _JIE:
            bi += 1
        if ss in spouse:
            spouse_root = True
    day = (chart.get("pillars") or {}).get("day") or {}
    day_ss = (day.get("shishenGan") or "").strip()
    if day_ss in _JIE:
        bi += 1

    if not spouse_root and cai + guan <= 1:
        return "weak_spouse"
    if bi >= 2 and (cai + guan) <= 1:
        return "rival_heavy"
    if (cai + guan) >= 2 or spouse_root:
        return "spouse_active"
    return "neutral"


_PROFILE_NARRATIVE: dict[str, dict[str, float]] = {
    "weak_spouse": {
        "single": 0.72,
        "dating": 0.55,
        "divorce": 0.25,
        "married": 0.30,
        "affair": 0.20,
    },
    "rival_heavy": {
        "single": 0.45,
        "dating": 0.40,
        "divorce": 0.55,
        "married": 0.35,
        "affair": 0.50,
    },
    "spouse_active": {
        "single": 0.25,
        "dating": 0.35,
        "divorce": 0.40,
        "married": 0.70,
        "affair": 0.45,
    },
    "neutral": {
        "single": 0.40,
        "dating": 0.45,
        "divorce": 0.35,
        "married": 0.55,
        "affair": 0.30,
    },
}


def score_marriage_narrative_option(
    chart: dict[str, Any],
    question: str,
    option_text: str,
) -> float:
    if any(k in (option_text or "") for k in _SINGLE_OPT):
        return score_marriage_single_option(chart, question, option_text)

    is_female = _chart_gender(chart) == "female"
    profile = _chart_marriage_profile(chart, is_female)
    tags = _narrative_tags(option_text)
    if not tags:
        return 0.30

    table = _PROFILE_NARRATIVE.get(profile, _PROFILE_NARRATIVE["neutral"])
    scores = [table.get(tag, 0.30) for tag in tags]
    base = sum(scores) / len(scores)

    years = parse_years_from_option(option_text)
    if years:
        year_scores = [
            score_marriage_year(chart, question, y, is_female=is_female)
            for y in years
        ]
        base = base * 0.35 + (sum(year_scores) / len(year_scores)) * 0.65

    q = question or ""
    if any(k in q for k in _DIVORCE_Q) and "divorce" in tags:
        base += 0.10
    if any(k in q for k in ("未婚", "单身", "从未")) and "single" in tags:
        base += 0.08
    if any(k in q for k in _AFFAIR_Q) and "affair" in tags:
        base += 0.10

    return min(max(base, 0.05), 1.0)


def score_marriage_option(
    chart: dict[str, Any],
    question: str,
    option: str,
    subtheme: MarriageSubtheme | None = None,
) -> float:
    st = subtheme or infer_marriage_subtheme(question, [option])
    _, text = _option_letter_and_text(option)
    if any(k in text for k in _SINGLE_OPT):
        return score_marriage_single_option(chart, question, text)
    years = parse_years_from_option(option)
    if years and (_is_year_only_option(text) or st == "marriage-year-event"):
        is_female = _chart_gender(chart) == "female"
        vals = [
            score_marriage_year(chart, question, y, is_female=is_female)
            for y in years
        ]
        return sum(vals) / len(vals)
    return score_marriage_narrative_option(chart, question, text)


def compute_marriage_score_margin(
    chart: dict[str, Any],
    question: str,
    options: list[str],
    subtheme: MarriageSubtheme | None = None,
) -> tuple[float, float]:
    """Return (top_score, margin_to_second)."""
    st = subtheme or infer_marriage_subtheme(question, options)
    if st != "marriage-year-event":
        return 0.0, 0.0
    scores: list[float] = []
    for opt in options:
        scores.append(score_marriage_option(chart, question, opt, subtheme=st))
    if not scores:
        return 0.0, 0.0
    ordered = sorted(scores, reverse=True)
    top = ordered[0]
    second = ordered[1] if len(ordered) > 1 else 0.0
    return top, top - second


def build_marriage_option_score_block(
    chart: dict[str, Any],
    question: str,
    options: list[str],
    subtheme: MarriageSubtheme | None = None,
) -> str:
    st = subtheme or infer_marriage_subtheme(question, options)
    if st != "marriage-year-event":
        return ""

    gender = _chart_gender(chart)
    star = "官杀" if gender == "female" else "财"
    rows: list[str] = []
    for opt in options:
        letter, text = _option_letter_and_text(opt)
        if any(k in text for k in _SINGLE_OPT):
            continue
        sc = score_marriage_option(chart, question, opt, subtheme=st)
        years = parse_years_from_option(opt)
        label = ",".join(str(y) for y in years) if years else text[:16]
        rows.append(f"{letter} {label} 规则分{sc:.2f}")
    if not rows:
        return ""

    top, margin = compute_marriage_score_margin(chart, question, options, subtheme=st)
    margin_note = ""
    if margin >= RULE_SCORE_MARGIN_STRONG and top >= RULE_SCORE_TOP_MIN:
        margin_note = (
            f"规则分最高领先{margin:.2f}, 可与排盘互证时优先参考; "
        )
    event = _event_kind(question)
    event_note = {
        "marry": "结婚/再婚年看配偶星透干与配偶宫合动",
        "divorce": "离婚/分居年看配偶宫冲刑与比劫夺财(男)/伤官见官(女)",
        "affair": "外遇/桃花年看偏财伤官动而配偶宫不稳",
    }.get(event, "须结合配偶星与配偶宫(日支)合冲")

    hint = (
        f"{'女命看官杀、男命看正财偏财' if gender else '按性别定配偶星(男财女官)'}; "
        f"{event_note}; {margin_note}"
        f"规则分仅供参考, 不得作为唯一依据; 分差<0.10时须主要靠排盘推理"
    )
    return f"【婚姻选项规则分】({hint}):\n" + "\n".join(rows)
