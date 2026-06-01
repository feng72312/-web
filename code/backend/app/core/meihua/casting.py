from __future__ import annotations

from app.core.liuyao.casting import cast_from_numbers, cast_from_time
from app.core.liuyao.models import LiuyaoInput
from app.core.meihua.models import MeihuaInput


def _to_liuyao_input(data: MeihuaInput) -> LiuyaoInput:
    return LiuyaoInput(
        question=data.question,
        method=data.method,
        numbers=data.numbers,
        year=data.year,
        month=data.month,
        day=data.day,
        hour=data.hour,
        minute=data.minute,
        second=data.second,
        calendar_type=data.calendar_type,
        is_leap_month=data.is_leap_month,
    )


def cast_meihua_lines(data: MeihuaInput) -> tuple[list[int], str]:
    liuyao = _to_liuyao_input(data)
    if data.method == "number":
        return cast_from_numbers(liuyao.numbers)
    if data.method == "time":
        return cast_from_time(liuyao)
    raise ValueError(f"unsupported method: {data.method}")
