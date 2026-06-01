from __future__ import annotations

from app.core.liuyao.models import LiuyaoInput
from app.schemas.paipan import PaipanRequest


def paipan_to_liuyao_input(body: PaipanRequest, question: str) -> LiuyaoInput:
    return LiuyaoInput(
        question=question.strip() or "论此命主所问之事",
        method="time",
        year=body.year,
        month=body.month,
        day=body.day,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        calendar_type=body.calendarType,
        is_leap_month=body.isLeapMonth,
    )
