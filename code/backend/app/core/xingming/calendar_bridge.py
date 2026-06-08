from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from lunar_python import Lunar, Solar

from app.core.calendar.china_dst import apply_china_dst
from app.core.qimen.solar_time import apply_true_solar_time, format_datetime
from app.core.tianxiang import ephemeris
from app.core.xingming.models import XingmingInput
from app.core.xingming.rules import XingmingRules


@dataclass
class XingmingCalendarContext:
    solar_label: str
    lunar_label: str
    true_solar_time: str
    utc_iso: str
    julian_day: float
    four_pillars: dict[str, str]
    gender_label: Literal["\u7537", "\u5973"]
    rules_applied: dict[str, str]
    latitude: float
    longitude: float


def _hour_to_time_index(hour: int, zi_hour_rule: str) -> int:
    if zi_hour_rule == "combined" and hour == 23:
        return 0
    if zi_hour_rule == "split" and hour == 23:
        return 12
    return (hour + 1) // 2


def _resolve_solar_datetime(data: XingmingInput, rules: XingmingRules) -> tuple[datetime, Solar, Lunar]:
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


def resolve_calendar(data: XingmingInput, rules: XingmingRules) -> XingmingCalendarContext:
    dt, solar, lunar = _resolve_solar_datetime(data, rules)
    _hour_to_time_index(dt.hour, rules.zi_hour_rule)
    cast_lunar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second).getLunar()
    ec = cast_lunar.getEightChar()
    utc_dt = dt.astimezone(timezone.utc)
    jd = ephemeris.datetime_to_julian(utc_dt)
    gender_label: Literal["\u7537", "\u5973"] = "\u7537" if data.gender == 1 else "\u5973"
    return XingmingCalendarContext(
        solar_label=solar.toYmdHms(),
        lunar_label=lunar.toString(),
        true_solar_time=format_datetime(dt),
        utc_iso=utc_dt.isoformat(),
        julian_day=jd,
        four_pillars={
            "year": ec.getYear(),
            "month": ec.getMonth(),
            "day": ec.getDay(),
            "hour": ec.getTime(),
        },
        gender_label=gender_label,
        rules_applied={
            **rules.as_meta(),
            "dstApplied": "true",
            "trueSolarApplied": "true" if data.use_true_solar_time else "false",
        },
        latitude=data.latitude,
        longitude=data.longitude,
    )
