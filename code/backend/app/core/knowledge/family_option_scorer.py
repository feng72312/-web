"""Deterministic family-origin option scores for MCQ hint blocks."""

from __future__ import annotations

from typing import Any

from app.core.knowledge.family_subtheme import FamilySubtheme, infer_family_subtheme
from app.core.knowledge.option_exclusion import _option_letter_and_text, _year_signals
from app.core.knowledge.target_year_block import _resolve_year_luck
from app.core.knowledge.year_option_scorer import (
    parse_years_from_option,
    score_year_option,
)


def _count_pillar_shishen(chart: dict[str, Any]) -> tuple[int, int, int, int]:
    cai = yin = bi = sha = 0
    for pillar in (chart.get("pillars") or {}).values():
        ss = (pillar.get("shishenGan") or "").strip()
        if ss in ("正财", "偏财"):
            cai += 1
        elif ss in ("正印", "偏印"):
            yin += 1
        elif ss in ("比肩", "劫财"):
            bi += 1
        elif ss in ("七杀", "正官"):
            sha += 1
    return cai, yin, bi, sha


def _chart_wealth_profile(chart: dict[str, Any]) -> str:
    cai, yin, bi, sha = _count_pillar_shishen(chart)
    if cai >= 2 and (yin + bi) <= 1 and sha >= 1:
        return "weak_cai_bias"
    if cai >= 2 and (yin + bi) <= 1:
        return "rich_bias"
    if cai == 0 and yin <= 1:
        return "poor_bias"
    return "mid_bias"


def _wealth_tier_from_text(text: str) -> str:
    t = text or ""
    if any(k in t for k in ("孤儿", "寄养", "孤儿院")):
        return "orphan"
    if any(k in t for k in ("亿万", "亿万家", "顶级富豪")):
        return "ultra_rich"
    if any(k in t for k in ("千万", "大富贵", "地主")):
        return "rich"
    if any(k in t for k in ("富贵", "富裕")):
        return "rich"
    if any(k in t for k in ("贫穷", "贫困", "贫寒", "赤贫")) or (
        "贫" in t and "富贵" not in t
    ):
        return "poor"
    if "小康" in t:
        return "mid"
    if any(k in t for k in ("普通", "中等", "一般", "盈余")):
        return "mid"
    return "unknown"


_TIER_SCORES: dict[str, dict[str, float]] = {
    "rich_bias": {
        "orphan": 0.1,
        "poor": 0.2,
        "mid": 0.45,
        "rich": 0.75,
        "ultra_rich": 0.65,
        "unknown": 0.3,
    },
    "poor_bias": {
        "orphan": 0.25,
        "poor": 0.7,
        "mid": 0.45,
        "rich": 0.25,
        "ultra_rich": 0.15,
        "unknown": 0.35,
    },
    "mid_bias": {
        "orphan": 0.15,
        "poor": 0.4,
        "mid": 0.65,
        "rich": 0.45,
        "ultra_rich": 0.3,
        "unknown": 0.35,
    },
    "weak_cai_bias": {
        "orphan": 0.2,
        "poor": 0.75,
        "mid": 0.55,
        "rich": 0.25,
        "ultra_rich": 0.15,
        "unknown": 0.35,
    },
}


def score_death_father_year(chart: dict[str, Any], year: int) -> float:
    dy, ln = _resolve_year_luck(chart, year)
    sig = _year_signals(chart, dy, ln)
    if not sig:
        return 0.2
    score = 0.25
    if sig.get("has_cai"):
        score += 0.15
    if sig.get("heavy_clash"):
        score += 0.3
    if sig.get("month_clash"):
        score += 0.1
    if sig.get("has_guansha"):
        score += 0.15
    if sig.get("has_yin") and not sig.get("heavy_clash"):
        score -= 0.2
    if sig.get("has_yin") and sig.get("has_cai") and not sig.get("heavy_clash"):
        score -= 0.1
    return min(max(score, 0.05), 1.0)


def score_death_mother_year(chart: dict[str, Any], year: int) -> float:
    dy, ln = _resolve_year_luck(chart, year)
    sig = _year_signals(chart, dy, ln)
    if not sig:
        return 0.2
    score = 0.25
    if sig.get("has_yin") and sig.get("heavy_clash"):
        score += 0.35
    elif sig.get("heavy_clash") and sig.get("has_cai"):
        score += 0.25
    elif sig.get("heavy_clash"):
        score += 0.2
    if sig.get("has_yin") and not sig.get("heavy_clash"):
        score -= 0.3
    if sig.get("has_shishang") and sig.get("has_yin") and not sig.get("heavy_clash"):
        score -= 0.15
    if sig.get("has_cai") and not sig.get("heavy_clash"):
        score -= 0.1
    return min(max(score, 0.05), 1.0)


def score_wealth_tier_option(chart: dict[str, Any], opt_text: str) -> float:
    tier = _wealth_tier_from_text(opt_text)
    profile = _chart_wealth_profile(chart)
    table = _TIER_SCORES.get(profile, _TIER_SCORES["mid_bias"])
    base = table.get(tier, 0.3)
    cai, yin, _, _sha = _count_pillar_shishen(chart)
    if tier == "orphan" and (cai >= 1 or yin >= 1):
        base -= 0.15
    if tier == "rich" and cai >= 2:
        base += 0.1
    if tier == "poor" and cai == 0:
        base += 0.1
    return min(max(base, 0.05), 1.0)


def score_family_option(
    chart: dict[str, Any],
    question: str,
    option: str,
    subtheme: FamilySubtheme | None = None,
) -> float:
    st = subtheme or infer_family_subtheme(question, [option])
    _, text = _option_letter_and_text(option)
    years = parse_years_from_option(option)
    if st == "family-death-father" and years:
        scores = [score_death_father_year(chart, y) for y in years]
        return sum(scores) / len(scores)
    if st == "family-death-mother" and years:
        scores = [score_death_mother_year(chart, y) for y in years]
        return sum(scores) / len(scores)
    if st == "family-wealth-tier":
        return score_wealth_tier_option(chart, text)
    if years:
        scores = [score_year_option(chart, question, y) for y in years]
        return sum(scores) / len(scores)
    tier = _wealth_tier_from_text(text)
    if tier != "unknown":
        return score_wealth_tier_option(chart, text)
    return 0.25


def build_family_option_score_block(
    chart: dict[str, Any],
    question: str,
    options: list[str],
    subtheme: FamilySubtheme | None = None,
) -> str:
    st = subtheme or infer_family_subtheme(question, options)
    if st is None:
        return ""
    if st == "family-relation":
        has_years = any(parse_years_from_option(o) for o in options)
        has_tier = any(
            _wealth_tier_from_text(_option_letter_and_text(o)[1]) != "unknown"
            for o in options
        )
        if not has_years and not has_tier:
            return ""
    rows: list[str] = []
    for opt in options:
        letter, text = _option_letter_and_text(opt)
        sc = score_family_option(chart, question, opt, subtheme=st)
        years = parse_years_from_option(opt)
        if years:
            year_label = ",".join(str(y) for y in years)
            rows.append(f"{letter} {year_label}年 规则分{sc:.2f}")
        else:
            label = text[:24] + ("..." if len(text) > 24 else "")
            rows.append(f"{letter} {label} 规则分{sc:.2f}")
    if not rows:
        return ""
    if st == "family-death-father":
        hint = (
            "丧父题重偏财冲合克; 冲根/合去之年不得仅因规则分低排除; "
            "规则分仅供与排盘互证, 不得单凭分数作答"
        )
    elif st == "family-death-mother":
        hint = (
            "丧母题重印星受克; 生扶合化助印之年通常非丧母; "
            "规则分仅供与排盘互证, 不得单凭分数作答"
        )
    elif st == "family-wealth-tier":
        hint = (
            "贫富题看年柱/月柱财星与父母星; 身弱财多倾向贫穷; "
            "规则分不得作为唯一依据, 勿仅因分高就选富贵/大富贵"
        )
    else:
        hint = "家庭关系题须与父母星/年月柱互证; 规则分仅供参考"
    return f"【家庭出身选项规则分】({hint}):\n" + "\n".join(rows)
