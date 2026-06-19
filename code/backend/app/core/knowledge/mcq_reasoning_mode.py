"""When Contest8 MCQ should use structured elimination reasoning."""

from __future__ import annotations

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.contest_channel_route import has_explicit_timing_signal
from app.core.knowledge.liunian_context import is_liunian_event_question
from app.core.knowledge.luck_prompt_util import extract_years_from_question, is_year_option_mcq

STRUCTURED_REASONING_THEMES: frozenset[str] = frozenset(
    {
        "流年事件",
        "婚姻感情",
        "健康疾病",
        "官非",
        "职业财运",
        "学历",
        "家庭出身",
        "子女",
        "田宅",
        "性格外貌",
    }
)

TIANHOU_OR_YONGSHEN_KEYS = (
    "用神",
    "调候",
    "寒暖",
    "燥湿",
    "喜神",
    "忌神",
    "格局",
    "体用",
    "通关",
    "清浊",
    "流通",
)

def should_structured_mcq_reasoning(question: str, options: list[str] | None = None) -> bool:
    text = (question or "").strip()
    if not text:
        return False
    theme = infer_question_theme(text)
    if theme in ("家庭出身", "子女") and not has_explicit_timing_signal(
        text, options
    ):
        if theme == "家庭出身":
            return True
        return False
    if theme == "学历" and not has_explicit_timing_signal(text, options):
        return True
    if is_liunian_event_question(text):
        return True
    if infer_question_theme(text) in STRUCTURED_REASONING_THEMES:
        return True
    if any(key in text for key in TIANHOU_OR_YONGSHEN_KEYS):
        return True
    if extract_years_from_question(text):
        return True
    timing_keys = ("哪一年", "何时", "虚龄", "大运", "运程", "年发生")
    if any(k in text for k in timing_keys) and options and is_year_option_mcq(options):
        return True
    return False
