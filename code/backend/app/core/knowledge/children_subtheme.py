"""Children (子女) MCQ sub-theme routing."""

from __future__ import annotations

from typing import Literal

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.luck_prompt_util import (
    is_year_option_mcq,
    parse_virtual_age_span,
)
from app.core.knowledge.option_exclusion import _option_letter_and_text

ChildrenSubtheme = Literal[
    "children-birth-year",
    "children-dayun-span",
    "children-status",
]

_BIRTH_Q_KEYS = (
    "哪年",
    "哪一年",
    "何时",
    "出生",
    "生孩子",
    "生子",
    "得到子女",
    "诞下",
)

_STATUS_Q_KEYS = (
    "婚恋",
    "子女情况",
    "子女运",
    "育有",
    "无子女",
    "几个孩子",
    "孩子数",
)

_NARRATIVE_KEYS = (
    "结婚",
    "离婚",
    "奉子",
    "未婚",
    "育有",
    "生一",
    "生二",
    "三子",
    "一女",
    "外宠",
    "发妻",
)


def _is_narrative_option(text: str) -> bool:
    t = text or ""
    if len(t) > 22:
        return True
    return any(k in t for k in _NARRATIVE_KEYS)


def _pure_year_options(options: list[str]) -> bool:
    if not is_year_option_mcq(options):
        return False
    for opt in options:
        _, text = _option_letter_and_text(opt)
        t = (text or "").strip()
        if t and not t.replace("年", "").strip().isdigit() and not t[:4].isdigit():
            if any(k in t for k in _NARRATIVE_KEYS):
                return False
    return True


def infer_children_subtheme(
    question: str,
    options: list[str] | None = None,
) -> ChildrenSubtheme | None:
    if infer_question_theme(question) != "子女":
        return None
    q = (question or "").strip()
    opts = list(options or [])

    if parse_virtual_age_span(q) and any(k in q for k in ("大运", "运程", "子女运")):
        return "children-dayun-span"

    narrative_n = sum(1 for opt in opts if _is_narrative_option(_option_letter_and_text(opt)[1]))
    if narrative_n >= 2 or any(k in q for k in _STATUS_Q_KEYS):
        if not _pure_year_options(opts):
            return "children-status"

    if _pure_year_options(opts) or any(k in q for k in _BIRTH_Q_KEYS):
        return "children-birth-year"

    if is_year_option_mcq(opts):
        return "children-birth-year"

    if narrative_n >= 1:
        return "children-status"

    return "children-birth-year"
