from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from lunar_python import Lunar, Solar

from app.core.calendar.china_dst import apply_china_dst
from app.core.qimen.solar_time import apply_true_solar_time, format_datetime
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules


@dataclass
class ZiweiCalendarContext:
    solar_label: str
    lunar_label: str
    true_solar_time: str
    four_pillars: dict[str, str]
    solar_date_str: str
    time_index: int
    gender_label: Literal["男", "女"]
    rules_applied: dict[str, str]


def _hour_to_time_index(hour: int, zi_hour_rule: str) -> int:
    if not 0 <= hour <= 23:
        raise ValueError("hour must be 0..23")
    if zi_hour_rule == "combined":
        if hour == 23:
            return 0
        return (hour + 1) // 2
    if hour == 23:
        return 12
    return (hour + 1) // 2


def _resolve_solar_datetime(data: ZiweiInput, rules: ZiweiRules) -> tuple[datetime, Solar, Lunar]:
    if data.calendar_type == "lunar":
        lunar_month = -data.month if data.is_leap_month else data.month
        lunar = Lunar.fromYmdHms(
            data.year,
            lunar_month,
            data.day,
            data.hour,
            data.minute,
            data.second,
        )
        solar = lunar.getSolar()
    else:
        solar = Solar.fromYmdHms(
            data.year,
            data.month,
            data.day,
            data.hour,
            data.minute,
            data.second,
        )
        lunar = solar.getLunar()

    ymd = solar.toYmdHms().split(" ")
    date_parts = ymd[0].split("-")
    time_parts = ymd[1].split(":")
    dt = datetime(
        int(date_parts[0]),
        int(date_parts[1]),
        int(date_parts[2]),
        int(time_parts[0]),
        int(time_parts[1]),
        int(time_parts[2]) if len(time_parts) > 2 else 0,
    )
    dt = apply_china_dst(dt)
    if data.use_true_solar_time:
        dt = apply_true_solar_time(dt, data.longitude)
    return dt, solar, lunar


def resolve_calendar(data: ZiweiInput, rules: ZiweiRules) -> ZiweiCalendarContext:
    dt, solar, lunar = _resolve_solar_datetime(data, rules)
    time_index = _hour_to_time_index(dt.hour, rules.zi_hour_rule)

    solar_date_str = f"{dt.year}-{dt.month}-{dt.day}"
    cast_lunar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second).getLunar()
    ec = cast_lunar.getEightChar()

    gender_label: Literal["男", "女"] = "男" if data.gender == 1 else "女"
    rules_applied = {
        **rules.as_meta(),
        "dstApplied": "true",
        "trueSolarApplied": "true" if data.use_true_solar_time else "false",
    }

    return ZiweiCalendarContext(
        solar_label=solar.toYmdHms(),
        lunar_label=lunar.toString(),
        true_solar_time=format_datetime(dt),
        four_pillars={
            "year": ec.getYear(),
            "month": ec.getMonth(),
            "day": ec.getDay(),
            "hour": ec.getTime(),
        },
        solar_date_str=solar_date_str,
        time_index=time_index,
        gender_label=gender_label,
        rules_applied=rules_applied,
    )
