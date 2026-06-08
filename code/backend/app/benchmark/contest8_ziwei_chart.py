"""Build Ziwei chart payload for Contest8 MCQ questions."""

from __future__ import annotations

from typing import Any

from app.benchmark.contest8_chart import gender_to_int
from app.benchmark.contest8_dataset import ContestQuestion
from app.config import settings
from app.core.knowledge.luck_prompt_util import extract_years_from_question
from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules

_engine = ZiweiEngine()


def _default_rules() -> ZiweiRules:
    return ZiweiRules(
        leap_month_rule=settings.ziwei_leap_month_rule,
        zi_hour_rule=settings.ziwei_zi_hour_rule,
        mutagen_table=settings.ziwei_mutagen_table,
    )


def resolve_target_year_for_question(q: ContestQuestion) -> int | None:
    years = extract_years_from_question(q.question)
    if years:
        return years[0]
    return None


def question_to_ziwei_input(q: ContestQuestion) -> ZiweiInput:
    birth = q.birth
    return ZiweiInput(
        name=q.person_name or "",
        calendar_type="solar",
        year=int(birth["year"]),
        month=int(birth["month"]),
        day=int(birth["day"]),
        hour=int(birth.get("hour", 0)),
        minute=int(birth.get("minute", 0)),
        second=0,
        gender=gender_to_int(q.gender),
        use_true_solar_time=True,
        longitude=float(birth.get("longitude", 120.0) or 120.0),
        target_year=resolve_target_year_for_question(q),
        question=q.question,
        rules=_default_rules(),
    )


def build_ziwei_chart_for_question(q: ContestQuestion) -> dict[str, Any]:
    return _engine.chart(question_to_ziwei_input(q)).to_dict()
