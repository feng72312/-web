"""Health / disease MCQ sub-theme routing."""

from __future__ import annotations

from typing import Literal

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.luck_prompt_util import (
    is_year_option_mcq,
    parse_dayun_ganzhi_from_question,
    parse_virtual_age_span,
)
from app.core.knowledge.option_exclusion import _option_letter_and_text
from app.core.knowledge.year_option_scorer import parse_years_from_option

HealthSubtheme = Literal[
    "health-year-event",
    "health-dayun-span",
    "health-diagnosis",
    "health-status",
]

_DAYUN_SPAN_Q_KEYS = (
    "大运期间",
    "大限",
    "大运",
)

_DISEASE_SPAN_Q_KEYS = (
    "疾病",
    "病患",
    "困扰",
    "健康",
)

_DIAGNOSIS_Q_KEYS = (
    "哪一种",
    "哪种",
    "器官",
    "手术",
    "诊断",
    "确诊",
    "疾病为",
    "什么病",
)

_TIMING_Q_KEYS = (
    "哪年",
    "哪一年",
    "何时",
    "什么时候",
    "于哪",
)

_STATUS_Q_KEYS = (
    "健康状况",
    "健康如何",
    "健康情况",
    "状况如何",
    "目前健康",
    "现时健康",
    "身体如何",
)


def _options_have_year_narrative(options: list[str]) -> bool:
    n = 0
    for opt in options:
        _, text = _option_letter_and_text(opt)
        if parse_years_from_option(text or ""):
            n += 1
    return n >= 2


def health_options_have_year_narrative(options: list[str]) -> bool:
    return _options_have_year_narrative(options)


def infer_health_subtheme(
    question: str,
    options: list[str] | None = None,
) -> HealthSubtheme | None:
    if infer_question_theme(question) != "健康疾病":
        return None
    q = (question or "").strip()
    opts = list(options or [])

    if parse_virtual_age_span(q) or (
        parse_dayun_ganzhi_from_question(q)
        and any(k in q for k in _DISEASE_SPAN_Q_KEYS)
    ):
        return "health-dayun-span"

    if any(k in q for k in _DAYUN_SPAN_Q_KEYS) and any(
        k in q for k in _DISEASE_SPAN_Q_KEYS
    ):
        return "health-dayun-span"

    if is_year_option_mcq(opts):
        return "health-year-event"

    if any(k in q for k in _TIMING_Q_KEYS):
        return "health-year-event"

    if any(k in q for k in _DIAGNOSIS_Q_KEYS):
        return "health-diagnosis"

    if _options_have_year_narrative(opts):
        return "health-status"

    if any(k in q for k in _STATUS_Q_KEYS):
        return "health-status"

    return "health-status"
