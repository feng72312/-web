from __future__ import annotations

from typing import Any

from app.api.helpers import request_to_input
from app.core.analysis.registry import AnalysisRegistry, build_default_registry
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.rules import PaipanRules
from app.benchmark.contest8_dataset import ContestQuestion
from app.config import settings
from app.schemas.paipan import PaipanRequest


def gender_to_int(gender: str) -> int:
    g = gender.strip().lower()
    return 1 if g in ("male", "m", "1") else 0


def question_to_paipan_request(q: ContestQuestion) -> PaipanRequest:
    birth = q.birth
    return PaipanRequest(
        name=q.person_name,
        calendarType="solar",
        year=int(birth["year"]),
        month=int(birth["month"]),
        day=int(birth["day"]),
        hour=int(birth.get("hour", 0)),
        minute=int(birth.get("minute", 0)),
        second=0,
        gender=gender_to_int(q.gender),
    )


def build_chart_for_question(
    q: ContestQuestion,
    engine: PaipanEngine | None = None,
    registry: AnalysisRegistry | None = None,
    *,
    include_luck_timeline: bool = True,
) -> dict[str, Any]:
    if engine is None:
        rules = PaipanRules(
            sect=settings.paipan_sect,
            early_zishi_mode=settings.early_zishi_mode,
        )
        engine = PaipanEngine(rules=rules)
    if registry is None:
        registry = build_default_registry()
    body = question_to_paipan_request(q)
    result = engine.calculate(
        request_to_input(body),
        include_luck_timeline=include_luck_timeline,
    )
    chart = result.to_dict()
    chart["gender"] = q.gender
    chart["birthYear"] = int(q.birth.get("year", 0))
    sections = registry.run_all(chart)
    chart["sections"] = sections
    if q.extra_info:
        chart["contestProfile"] = q.extra_info
    return chart
