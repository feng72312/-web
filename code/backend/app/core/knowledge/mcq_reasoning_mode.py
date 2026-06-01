"""When Contest8 MCQ should use structured elimination reasoning."""

from __future__ import annotations

import re

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.liunian_context import is_liunian_event_question
from app.core.knowledge.luck_prompt_util import extract_years_from_question

STRUCTURED_REASONING_THEMES: frozenset[str] = frozenset(
    {"流年事件", "婚姻感情", "健康疾病", "官非"}
)

_YEAR_IN_OPTION = re.compile(r"(?:^|\s)(19|20)\d{2}(?:\s*年)?", re.MULTILINE)


def is_year_option_mcq(options: list[str]) -> bool:
    count = 0
    for opt in options:
        if _YEAR_IN_OPTION.search(opt or ""):
            count += 1
    return count >= 2


def should_structured_mcq_reasoning(question: str, options: list[str] | None = None) -> bool:
    text = (question or "").strip()
    if not text:
        return False
    if is_liunian_event_question(text):
        return True
    if infer_question_theme(text) in STRUCTURED_REASONING_THEMES:
        return True
    if extract_years_from_question(text):
        return True
    timing_keys = ("哪一年", "何时", "虚龄", "大运", "运程", "年发生")
    if any(k in text for k in timing_keys) and options and is_year_option_mcq(options):
        return True
    return False
