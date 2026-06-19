"""Career / wealth MCQ sub-theme routing."""

from __future__ import annotations

import re
from typing import Literal

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.luck_prompt_util import (
    is_year_option_mcq,
    parse_virtual_age_span,
)
from app.core.knowledge.option_exclusion import _option_letter_and_text

CareerSubtheme = Literal[
    "wealth",
    "career-year-event",
    "career-status",
    "major-industry",
]

_MAJOR_Q_KEYS = (
    "科系",
    "读什么科",
    "主修",
    "系别",
)

_WEALTH_Q_KEYS = (
    "财运",
    "身家",
    "收入",
    "年薪",
    "负债",
    "欠债",
    "买房",
    "置业",
    "资产",
    "发财",
    "横财",
    "理财",
    "财富",
    "钱财",
    "存款",
    "薪酬",
    "投资",
    "赚钱",
    "富有",
    "贫穷",
    "经济",
    "财务",
    "理财",
)

_TIMING_Q_KEYS = (
    "哪年",
    "哪一年",
    "何时",
    "什么时候",
    "于哪",
    "哪一年",
    "年间",
    "期间",
)

_CAREER_EVENT_Q_KEYS = (
    "创业",
    "失业",
    "转行",
    "升职",
    "突破",
    "变动",
    "变化",
    "事业",
    "工作",
    "职业",
    "从业",
    "大运",
    "虚龄",
)

_STATUS_Q_KEYS = (
    "目前",
    "现在",
    "现职",
    "从事",
    "职业是",
    "工作性质",
    "行业",
    "职位",
    "职业运",
    "外貌",
    "性格",
)


def _has_wealth_signal(question: str, options: list[str]) -> bool:
    q = question or ""
    if any(k in q for k in _WEALTH_Q_KEYS):
        return True
    wealth_n = 0
    for opt in options:
        _, text = _option_letter_and_text(opt)
        t = text or ""
        if any(k in t for k in ("负债", "欠债", "发财", "投资", "理财", "身家", "收入")):
            wealth_n += 1
    return wealth_n >= 2


def _narrative_career_options(options: list[str]) -> bool:
    keys = (
        "老板",
        "打工",
        "创业",
        "失业",
        "公司",
        "职员",
        "教师",
        "律师",
        "医生",
        "公务员",
        "自由",
        "行业",
    )
    n = 0
    for opt in options:
        _, text = _option_letter_and_text(opt)
        t = text or ""
        if len(t) > 18 or any(k in t for k in keys):
            n += 1
    return n >= 2


def infer_career_subtheme(
    question: str,
    options: list[str] | None = None,
) -> CareerSubtheme | None:
    if infer_question_theme(question) != "职业财运":
        return None
    q = (question or "").strip()
    opts = list(options or [])

    if any(k in q for k in _MAJOR_Q_KEYS):
        return "major-industry"

    if _has_wealth_signal(q, opts):
        return "wealth"

    if parse_virtual_age_span(q) and any(k in q for k in _CAREER_EVENT_Q_KEYS):
        return "career-year-event"

    if is_year_option_mcq(opts):
        return "career-year-event"

    if any(k in q for k in _TIMING_Q_KEYS) and any(
        k in q for k in _CAREER_EVENT_Q_KEYS
    ):
        return "career-year-event"

    for opt in opts:
        _, text = _option_letter_and_text(opt)
        if any(k in (text or "") for k in ("年", "岁")) and _year_in_option(text or ""):
            return "career-year-event"

    if any(k in q for k in ("年", "岁")) and any(k in q for k in _CAREER_EVENT_Q_KEYS):
        return "career-year-event"

    if _narrative_career_options(opts) and any(k in q for k in ("年", "岁", "期间")):
        return "career-year-event"

    if any(k in q for k in _STATUS_Q_KEYS):
        return "career-status"

    return "career-status"


def _year_in_option(text: str) -> bool:
    return bool(re.search(r"(19|20)\d{2}", text or ""))
