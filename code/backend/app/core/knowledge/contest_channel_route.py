"""Route Contest8 MCQ to full judgement chain vs timing (应期) channel."""

from __future__ import annotations

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.liunian_context import is_liunian_event_question
from app.core.knowledge.luck_prompt_util import (
    extract_years_from_question,
    is_year_option_mcq,
    parse_virtual_age_span,
)

# 感情/健康: keep full BaziJudgementChain + conservative guard (unchanged).
FULL_JUDGEMENT_THEMES: frozenset[str] = frozenset({"婚姻感情", "健康疾病"})

# 静态主导题型: 无明确应期信号时不走 yingqi / 结构化岁运长推理.
STATIC_DOMINANT_THEMES: frozenset[str] = frozenset({"学历", "家庭出身", "子女"})

_YINGQI_TEXT_KEYS = (
    "流年",
    "大运",
    "虚龄",
    "运程",
    "哪一年",
    "哪年",
    "那年",
    "何时",
    "岁运",
    "并临",
    "太岁",
    "年发生",
    "大限",
)


def has_explicit_timing_signal(
    question: str,
    options: list[str] | None = None,
) -> bool:
    """Gregorian year, virtual-age span, dayun/liunian keywords, or year-style options."""
    text = (question or "").strip()
    if not text:
        return False
    if parse_virtual_age_span(text):
        return True
    if extract_years_from_question(text):
        return True
    if is_liunian_event_question(text):
        return True
    if any(k in text for k in _YINGQI_TEXT_KEYS):
        return True
    if options and is_year_option_mcq(options):
        return True
    return False


def is_static_dominant_without_timing(
    question: str,
    options: list[str] | None = None,
) -> bool:
    theme = infer_question_theme(question)
    return theme in STATIC_DOMINANT_THEMES and not has_explicit_timing_signal(
        question, options
    )


def uses_full_judgement_chain(question: str, options: list[str] | None = None) -> bool:
    """True -> run full judgement chain and inject all judge opinions."""
    return infer_question_theme(question) in FULL_JUDGEMENT_THEMES


def resolve_contest_votes(
    question: str,
    options: list[str] | None,
    votes: int,
) -> int:
    """Default votes=3 for full (marriage/health) when CLI leaves votes at 1."""
    n = max(1, min(int(votes), 5))
    if n > 1:
        return n
    if uses_full_judgement_chain(question, options):
        return 3
    return 1


def is_yingqi_question(question: str, options: list[str] | None = None) -> bool:
    """
    Timing questions (流年/虚龄/大运/择年): use lightweight suiyun prompt,
    skip full judgement pre-conclusions and conservative guard.
    """
    if uses_full_judgement_chain(question, options):
        return False
    text = (question or "").strip()
    if not text:
        return False
    theme = infer_question_theme(text)
    if theme in STATIC_DOMINANT_THEMES:
        return has_explicit_timing_signal(text, options)
    if theme == "流年事件":
        return True
    return has_explicit_timing_signal(text, options)

