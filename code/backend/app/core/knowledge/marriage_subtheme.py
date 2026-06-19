"""Marriage / relationship MCQ sub-theme routing."""

from __future__ import annotations

from typing import Literal

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.luck_prompt_util import is_year_option_mcq
from app.core.knowledge.option_exclusion import _option_letter_and_text

MarriageSubtheme = Literal[
    "marriage-year-event",
    "marriage-status",
    "marriage-narrative",
    "marriage-affair",
]

_AFFAIR_Q_KEYS = (
    "外遇",
    "桃花",
    "同性恋",
    "私情",
    "情人",
    "第三者",
    "同居",
    "劈腿",
)

_STATUS_Q_KEYS = (
    "截至",
    "目前",
    "现在",
    "至今",
    "状况",
    "情况如何",
    "感情婚姻",
    "婚姻状况",
)

_TIMING_Q_KEYS = (
    "哪年",
    "哪一年",
    "何时",
    "什么时候",
    "于哪",
    "哪一年结婚",
    "哪一年离婚",
    "哪一年再婚",
)

_NARRATIVE_OPT_KEYS = (
    "结婚",
    "离婚",
    "再婚",
    "分居",
    "未婚",
    "单身",
    "外遇",
    "美满",
    "恋爱",
    "奉子",
    "同居",
    "同性恋",
    "从未",
    "独身",
    "配偶",
    "丈夫",
    "妻子",
)


def _is_narrative_option(text: str) -> bool:
    t = text or ""
    if len(t) > 20:
        return True
    return any(k in t for k in _NARRATIVE_OPT_KEYS)


def _pure_year_options(options: list[str]) -> bool:
    if not is_year_option_mcq(options):
        return False
    for opt in options:
        _, text = _option_letter_and_text(opt)
        t = (text or "").strip()
        if t and _is_narrative_option(t):
            return False
    return True


def _affair_from_options(options: list[str]) -> bool:
    affair_n = 0
    for opt in options:
        _, text = _option_letter_and_text(opt)
        if any(k in (text or "") for k in _AFFAIR_Q_KEYS):
            affair_n += 1
    return affair_n >= 2


def infer_marriage_subtheme(
    question: str,
    options: list[str] | None = None,
) -> MarriageSubtheme | None:
    if infer_question_theme(question) != "婚姻感情":
        return None
    q = (question or "").strip()
    opts = list(options or [])

    if any(k in q for k in _AFFAIR_Q_KEYS) or _affair_from_options(opts):
        return "marriage-affair"

    narrative_n = sum(
        1 for opt in opts if _is_narrative_option(_option_letter_and_text(opt)[1])
    )

    if any(k in q for k in _STATUS_Q_KEYS):
        return "marriage-status"

    if narrative_n >= 1 and not _pure_year_options(opts):
        return "marriage-narrative"

    if narrative_n >= 2:
        return "marriage-narrative"

    if _pure_year_options(opts):
        return "marriage-year-event"

    if any(k in q for k in _TIMING_Q_KEYS):
        return "marriage-year-event"

    if narrative_n >= 1:
        return "marriage-narrative"

    return "marriage-narrative"
