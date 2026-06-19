"""Family-origin MCQ sub-theme routing (within infer_question_theme == 家庭出身)."""

from __future__ import annotations

from typing import Literal

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.luck_prompt_util import is_year_option_mcq
from app.core.knowledge.option_exclusion import _option_letter_and_text

FamilySubtheme = Literal[
    "family-death-father",
    "family-death-mother",
    "family-wealth-tier",
    "family-relation",
]

_DEATH_KEYS = ("去世", "离世", "仙逝", "过世", "逝世", "离弃", "丧父", "丧母")
_TIMING_KEYS = ("哪年", "何时", "于哪", "什么时候", "哪一年")

_WEALTH_Q_KEYS = (
    "贫或富",
    "出身贫",
    "家境如何",
    "家境",
    "身家",
    "大富贵",
    "富贵家庭",
    "贫穷家庭",
    "小康之家",
    "孤儿院",
    "贫富",
)

_WEALTH_OPT_KEYS = (
    "贫穷",
    "贫困",
    "贫寒",
    "富贵",
    "富裕",
    "小康",
    "孤儿",
    "寄养",
    "千万",
    "亿万",
    "大富贵",
)


def _asks_father(q: str) -> bool:
    if "父亲" in q or "父星" in q or "丧父" in q:
        return True
    if "父" in q and "父母" not in q and "母" not in q:
        return True
    return False


def _asks_mother(q: str) -> bool:
    if "母亲" in q or "母星" in q or "丧母" in q:
        return True
    if "母" in q and "父母" not in q and "父" not in q:
        return True
    return False


def _is_death_question(q: str) -> bool:
    if any(k in q for k in _DEATH_KEYS):
        return True
    return any(k in q for k in _TIMING_KEYS) and ("父" in q or "母" in q)


_NARRATIVE_KEYS = ("从商", "当官", "企业", "改嫁", "守寡", "干部", "政府", "弟", "兄", "姐", "妹", "外婆", "照顾")


def _is_narrative_option(text: str) -> bool:
    t = text or ""
    if len(t) > 18:
        return True
    return any(k in t for k in _NARRATIVE_KEYS)


def _option_death_father(text: str) -> bool:
    t = text or ""
    return "父亲" in t and any(k in t for k in _DEATH_KEYS)


def _option_death_mother(text: str) -> bool:
    t = text or ""
    return "母亲" in t and any(k in t for k in _DEATH_KEYS)


def _death_from_options(options: list[str]) -> FamilySubtheme | None:
    father = mother = 0
    for opt in options:
        _, text = _option_letter_and_text(opt)
        if _option_death_father(text):
            father += 1
        if _option_death_mother(text):
            mother += 1
    if mother > father and mother >= 1:
        return "family-death-mother"
    if father >= 1:
        return "family-death-father"
    return None


def _mixed_wealth_narrative_options(options: list[str]) -> bool:
    tier_n = narrative_n = 0
    for opt in options:
        _, text = _option_letter_and_text(opt)
        if _wealth_tier_from_text(text) != "unknown":
            tier_n += 1
        if _is_narrative_option(text):
            narrative_n += 1
    return tier_n >= 1 and narrative_n >= 1


def _wealth_tier_from_text(text: str) -> str:
    t = text or ""
    if any(k in t for k in ("孤儿", "寄养", "孤儿院")):
        return "orphan"
    if any(k in t for k in ("贫穷", "贫困", "贫寒", "赤贫")) or (
        "贫" in t and "富贵" not in t
    ):
        return "poor"
    if any(k in t for k in ("富贵", "富裕", "千万", "亿万", "大富贵")):
        return "rich"
    if "小康" in t:
        return "mid"
    return "unknown"


def _is_wealth_tier_question(q: str, options: list[str] | None) -> bool:
    if any(
        k in q
        for k in ("关系", "状况", "情况如何", "背景", "疼爱", "离异", "吵闹", "和谐")
    ):
        if not any(k in q for k in ("贫", "富", "小康", "富贵", "身家", "孤儿", "身家")):
            return False
    if any(k in q for k in _WEALTH_Q_KEYS):
        return True
    tier_count = 0
    for opt in options or []:
        _, text = _option_letter_and_text(opt)
        if _wealth_tier_from_text(text) != "unknown":
            tier_count += 1
    if tier_count >= 3:
        return True
    opts_text = " ".join(options or [])
    return sum(1 for k in _WEALTH_OPT_KEYS if k in opts_text) >= 2


def infer_family_subtheme(
    question: str,
    options: list[str] | None = None,
) -> FamilySubtheme | None:
    if infer_question_theme(question) != "家庭出身":
        return None
    q = (question or "").strip()
    opts = list(options or [])

    death_from_opts = _death_from_options(opts)
    if death_from_opts:
        return death_from_opts

    if _mixed_wealth_narrative_options(opts) or sum(
        1 for opt in opts if _is_narrative_option(_option_letter_and_text(opt)[1])
    ) >= 2:
        return "family-relation"

    if _asks_mother(q) and not _asks_father(q):
        if _is_death_question(q) or (
            is_year_option_mcq(opts) and not _is_wealth_tier_question(q, opts)
        ):
            return "family-death-mother"

    if _asks_father(q) and not _asks_mother(q):
        if _is_death_question(q) or (
            is_year_option_mcq(opts) and not _is_wealth_tier_question(q, opts)
        ):
            return "family-death-father"

    if _asks_mother(q) and _asks_father(q) and _is_death_question(q):
        if "母" in q[: max(q.find("父"), 0) + 20] or q.find("母") < q.find("父"):
            return "family-death-mother"
        return "family-death-father"

    if _is_wealth_tier_question(q, opts):
        return "family-wealth-tier"

    return "family-relation"
