"""Rule-based option pre-exclusion for liunian event MCQ (soft hints, not final answers)."""

from __future__ import annotations

import re
from typing import Any

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.luck_prompt_util import (
    extract_years_from_question,
    resolve_target_year_from_chart,
)
from app.core.knowledge.target_year_block import _resolve_year_luck

# (tag, keywords in option text)
OPTION_TAGS: list[tuple[str, tuple[str, ...]]] = [
    ("guanfei", ("坐牢", "犯法", "官非", "警察", "刑事", "牢狱", "扣留", "被抓")),
    ("health", ("病", "癌", "手术", "住院", "骨折", "受伤", "忧郁", "服药", "乳")),
    ("windfall", ("横财", "中奖", "意外之财", "小横财", "发一笔")),
    ("wealth_loss", ("破财", "亏损", "股票损失", "负债", "损失")),
    ("career", ("工作", "创业", "升职", "生意", "合伙", "经营")),
    ("marriage", ("结婚", "离婚", "外遇", "私情", "妻子", "丈夫", "同居", "再婚")),
    ("divorce", ("离婚", "分手", "分居", "搬离")),
    ("single", ("单身", "未婚", "从未结婚", "光棍")),
    ("study", ("学历", "大学", "读书", "毕业", "学校", "专科", "博士", "硕士")),
    ("sport", ("冠军", "比赛", "象棋", "获奖")),
]


def _option_letter_and_text(opt: str) -> tuple[str, str]:
    s = opt.strip()
    letter = s[:1].upper() if s else "?"
    text = s[2:].strip() if len(s) > 2 else s
    return letter, text


def _tag_option_text(text: str) -> set[str]:
    tags: set[str] = set()
    for tag, keys in OPTION_TAGS:
        if any(k in text for k in keys):
            tags.add(tag)
    return tags


def _hide_shishen_set(hide_stems: list[str]) -> set[str]:
    found: set[str] = set()
    for item in hide_stems:
        m = re.search(r"\(([^)]+)\)", item)
        if m:
            found.add(m.group(1).strip())
    return found


def _year_signals(
    chart: dict[str, Any],
    dy: dict[str, Any] | None,
    ln: dict[str, Any] | None,
) -> dict[str, bool]:
    if not ln:
        return {}
    ln_p = ln.get("pillar") or {}
    dy_p = (dy or {}).get("pillar") or {}
    ln_ss = ln_p.get("shishenGan", "")
    dy_ss = dy_p.get("shishenGan", "")
    hide = _hide_shishen_set(ln_p.get("hideStems") or [])
    all_ss = hide | {x for x in (ln_ss, dy_ss) if x}

    pillars = chart.get("pillars") or {}
    lg, lz = ln_p.get("gan", ""), ln_p.get("zhi", "")
    day = pillars.get("day") or {}
    day_zhi = day.get("zhi", "")
    month = pillars.get("month") or {}
    month_zhi = month.get("zhi", "")

    from app.core.paipan.interactions import ZHI_CHONG

    def _chong(a: str, b: str) -> bool:
        if not a or not b:
            return False
        for x, y in ZHI_CHONG:
            if (a, b) in ((x, y), (y, x)):
                return True
        return False

    day_clash = _chong(day_zhi, lz)
    month_clash = _chong(month_zhi, lz)
    chong_count = sum(1 for x in (day_clash, month_clash) if x)

    return {
        "has_guansha": bool(all_ss & {"七杀", "正官"}),
        "has_cai": bool(all_ss & {"偏财", "正财"}),
        "has_yin": bool(all_ss & {"正印", "偏印"}),
        "has_shishang": bool(all_ss & {"食神", "伤官"}),
        "has_jiebi": bool(all_ss & {"比肩", "劫财"}),
        "day_clash": day_clash,
        "month_clash": month_clash,
        "heavy_clash": chong_count >= 1,
        "ln_ss": ln_ss,
    }


def _judge_option(tags: set[str], sig: dict[str, bool], theme: str) -> tuple[str, str]:
    """Return (倾向保留|倾向排除|待核), reason."""
    if not sig:
        return "待核", "无目标年流年数据"

    reasons_exclude: list[str] = []
    reasons_keep: list[str] = []

    if "guanfei" in tags:
        if sig.get("has_guansha") or (sig.get("heavy_clash") and sig.get("has_jiebi")):
            reasons_keep.append("官杀或冲劫, 可承载官非压力")
        elif sig.get("has_cai") and sig.get("heavy_clash"):
            reasons_keep.append("财年逢冲, 可因财招刑或官非")
        elif sig.get("has_cai"):
            reasons_keep.append("财旺之年亦可因财致祸入狱, 勿仅选横财")
        elif sig.get("has_yin") and not sig.get("heavy_clash"):
            reasons_exclude.append("印星为主, 无强冲, 官非类象偏弱")

    if "windfall" in tags:
        if sig.get("has_cai") and not sig.get("has_guansha") and not sig.get("heavy_clash"):
            reasons_exclude.append("纯财年勿断横财, 优先考虑刑灾官非或破耗")
        elif sig.get("has_cai") and sig.get("has_guansha"):
            reasons_exclude.append("官杀财杂, 横财类象偏弱")
        elif sig.get("has_guansha") and not sig.get("has_cai"):
            reasons_exclude.append("官杀压身, 非典型横财")
        elif sig.get("has_yin") or sig.get("has_shishang"):
            reasons_exclude.append("印食伤年, 非典型横财")

    if "health" in tags:
        if sig.get("has_yin") and sig.get("heavy_clash"):
            reasons_keep.append("印星逢冲, 可论健康")
        elif sig.get("has_guansha") and sig.get("heavy_clash"):
            reasons_keep.append("官杀逢冲, 可论疾伤")
        elif sig.get("has_cai") and not sig.get("heavy_clash"):
            reasons_exclude.append("财年无强冲, 重病类象偏弱")
        elif sig.get("has_cai") and sig.get("heavy_clash"):
            reasons_exclude.append("财年逢冲多主财事刑灾, 重病类象偏弱")

    if "wealth_loss" in tags:
        if sig.get("has_jiebi") or (sig.get("has_cai") and sig.get("heavy_clash")):
            reasons_keep.append("比劫或财逢冲, 可论破耗")
        elif sig.get("has_yin"):
            reasons_exclude.append("印年, 破耗类象偏弱")

    if "sport" in tags:
        if sig.get("has_shishang"):
            reasons_keep.append("食伤年, 可论技艺比赛")
        else:
            reasons_exclude.append("非食伤主事, 比赛夺冠类象偏弱")

    if "marriage" in tags and theme in ("流年事件", "婚姻感情"):
        if sig.get("has_cai") or sig.get("has_guansha"):
            reasons_keep.append("财或官杀引动, 可论感情")
        elif sig.get("has_shishang") and sig.get("heavy_clash"):
            reasons_keep.append("食伤逢冲, 可论感情变动")
        else:
            reasons_exclude.append("流年十神少配偶星, 感情类象偏弱")

    if "divorce" in tags and theme == "婚姻感情":
        if sig.get("heavy_clash") and (sig.get("has_cai") or sig.get("has_jiebi")):
            reasons_keep.append("冲合财劫, 可论婚变")
        elif sig.get("has_yin") and not sig.get("heavy_clash"):
            reasons_exclude.append("印年无强冲, 离婚类象偏弱")

    if "single" in tags and theme == "婚姻感情":
        if sig.get("has_cai") or sig.get("has_guansha"):
            reasons_exclude.append("财官杀引动, 单身类象偏弱")
        elif sig.get("has_yin") or sig.get("has_shishang"):
            reasons_keep.append("印或食伤为主, 可论独处")

    if theme == "官非" and "guanfei" in tags:
        if sig.get("has_guansha") or (sig.get("heavy_clash") and sig.get("has_jiebi")):
            reasons_keep.append("官杀或冲劫, 官非类象强")
        elif sig.get("has_yin") and not sig.get("heavy_clash"):
            reasons_exclude.append("印年无冲, 官非偏弱")

    if theme == "学历" and "study" in tags:
        if sig.get("has_yin"):
            reasons_keep.append("印星流年, 可论学业")
        elif sig.get("has_shishang") and not sig.get("has_yin"):
            reasons_exclude.append("食伤无印, 高学历类象偏弱")

    if reasons_exclude and not reasons_keep:
        return "倾向排除", "; ".join(reasons_exclude)
    if reasons_keep and not reasons_exclude:
        return "倾向保留", "; ".join(reasons_keep)
    if reasons_exclude and reasons_keep:
        return "待核", f"保留:{reasons_keep[0]}; 排除:{reasons_exclude[0]}"
    return "待核", f"流年十神{sig.get('ln_ss','')}, 请结合题干核对"


def build_option_exclusion_block(
    chart: dict[str, Any],
    question: str,
    options: list[str],
) -> str:
    if not options:
        return ""
    theme = infer_question_theme(question)
    year = resolve_target_year_from_chart(chart, question)
    if year is None:
        if theme not in ("婚姻感情", "健康疾病", "官非", "流年事件"):
            return ""
        lines = [
            "【规则预排除】(无明确目标年, 仅按选项类象与本命线索, 须在【选项排除】中论证):",
        ]
        for opt in options:
            letter, text = _option_letter_and_text(opt)
            tags = _tag_option_text(text)
            if tags:
                lines.append(f"{letter}: 待核 - 类象{','.join(sorted(tags))}, 须对照配偶星/疾厄/官杀")
            else:
                lines.append(f"{letter}: 待核 - 未识别类象")
        return "\n".join(lines)
    dy, ln = _resolve_year_luck(chart, year)
    sig = _year_signals(chart, dy, ln)
    if not sig:
        return ""

    lines = [
        "【规则预排除】(由流年十神/冲合与选项类象对照, 可在【选项排除】中推翻):",
        f"目标年{year} 流年十神{sig.get('ln_ss','')} "
        f"官杀={sig.get('has_guansha')} 财={sig.get('has_cai')} "
        f"印={sig.get('has_yin')} 食伤={sig.get('has_shishang')} "
        f"冲日支={sig.get('day_clash')}",
    ]
    keep_letters: list[str] = []
    drop_letters: list[str] = []
    for opt in options:
        letter, text = _option_letter_and_text(opt)
        tags = _tag_option_text(text)
        if not tags:
            lines.append(f"{letter}: 待核 - 未识别选项类象, 须人工对照")
            continue
        verdict, reason = _judge_option(tags, sig, theme)
        lines.append(f"{letter}: {verdict} - {reason}")
        if verdict == "倾向保留":
            keep_letters.append(letter)
        elif verdict == "倾向排除":
            drop_letters.append(letter)
    if len(keep_letters) == 1:
        lines.append(f"提示: 仅 {keep_letters[0]} 倾向保留, 结论应优先论证该项.")
    elif keep_letters:
        lines.append(f"提示: 优先在 {','.join(keep_letters)} 中细选.")
    if len(drop_letters) >= 3:
        lines.append(f"提示: {','.join(drop_letters)} 倾向排除, 勿凭常见叙事选其一.")
    return "\n".join(lines)
