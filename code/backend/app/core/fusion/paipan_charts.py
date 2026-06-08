from __future__ import annotations

from app.config import settings
from app.core.xingming.engine import XingmingEngine
from app.core.xingming.models import XingmingInput
from app.core.xingming.rules import XingmingRules
from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules
from app.schemas.paipan import PaipanRequest

_ziwei_engine = ZiweiEngine()
_xingming_engine = XingmingEngine()


def paipan_to_ziwei_input(body: PaipanRequest, question: str = "") -> ZiweiInput:
    return ZiweiInput(
        name=body.name,
        calendar_type=body.calendarType,  # type: ignore[arg-type]
        year=body.year,
        month=body.month,
        day=body.day,
        is_leap_month=body.isLeapMonth,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        gender=body.gender,
        use_true_solar_time=True,
        longitude=120.0,
        target_year=None,
        question=question or body.question,
        rules=ZiweiRules(
            leap_month_rule=settings.ziwei_leap_month_rule,
            zi_hour_rule=settings.ziwei_zi_hour_rule,
            mutagen_table=settings.ziwei_mutagen_table,
        ),
    )


def paipan_to_xingming_input(body: PaipanRequest, question: str = "") -> XingmingInput:
    return XingmingInput(
        name=body.name,
        calendar_type=body.calendarType,  # type: ignore[arg-type]
        year=body.year,
        month=body.month,
        day=body.day,
        is_leap_month=body.isLeapMonth,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        gender=body.gender,
        use_true_solar_time=True,
        longitude=120.0,
        latitude=35.0,
        target_year=None,
        question=question or body.question,
        rules=XingmingRules(),
    )


def build_ziwei_chart_from_paipan(body: PaipanRequest, question: str = "") -> dict:
    return _ziwei_engine.chart(paipan_to_ziwei_input(body, question)).to_dict()


def build_xingming_chart_from_paipan(body: PaipanRequest, question: str = "") -> dict:
    return _xingming_engine.chart(paipan_to_xingming_input(body, question)).to_dict()
