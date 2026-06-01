from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from lunar_python import Lunar, Solar

from app.core.liuren.solar_time import apply_true_solar_time

JIEQI_S2T: dict[str, str] = {
    "立春": "立春",
    "雨水": "雨水",
    "惊蛰": "驚蟄",
    "春分": "春分",
    "清明": "清明",
    "谷雨": "穀雨",
    "立夏": "立夏",
    "小满": "小滿",
    "芒种": "芒種",
    "夏至": "夏至",
    "小暑": "小暑",
    "大暑": "大暑",
    "立秋": "立秋",
    "处暑": "處暑",
    "白露": "白露",
    "秋分": "秋分",
    "寒露": "寒露",
    "霜降": "霜降",
    "立冬": "立冬",
    "小雪": "小雪",
    "大雪": "大雪",
    "冬至": "冬至",
    "小寒": "小寒",
    "大寒": "大寒",
}


@dataclass
class LiurenCalendarContext:
    jieqi: str
    lunar_month: str
    day_ganzhi: str
    hour_ganzhi: str
    four_pillars: dict[str, str]
    hour_zhi: str
    true_solar_time: str
    civil_time: str


def resolve_calendar(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    calendar_type: str,
    is_leap_month: bool,
    use_true_solar_time: bool,
    longitude: float,
) -> LiurenCalendarContext:
    if calendar_type == "lunar":
        lunar = Lunar.fromYmdHms(year, month, day, hour, minute, second)
        solar = lunar.getSolar()
        dt = datetime(
            solar.getYear(),
            solar.getMonth(),
            solar.getDay(),
            solar.getHour(),
            solar.getMinute(),
            solar.getSecond(),
        )
    else:
        dt = datetime(year, month, day, hour, minute, second)
        lunar = Solar.fromYmdHms(year, month, day, hour, minute, second).getLunar()

    civil = dt.strftime("%Y-%m-%d %H:%M:%S")
    if use_true_solar_time:
        dt = apply_true_solar_time(dt, longitude)

    lunar_cast = Solar.fromYmdHms(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
    ).getLunar()
    ec = lunar_cast.getEightChar()
    ec.setSect(2)

    prev_jq = lunar_cast.getPrevJieQi()
    jq_name = prev_jq.getName() if prev_jq else ""
    jieqi = JIEQI_S2T.get(jq_name, jq_name)

    lunar_month = lunar_cast.getMonthInChinese()
    day_gz = ec.getDay()
    hour_gz = ec.getTime()

    return LiurenCalendarContext(
        jieqi=jieqi,
        lunar_month=lunar_month,
        day_ganzhi=day_gz,
        hour_ganzhi=hour_gz,
        four_pillars={
            "year": ec.getYear(),
            "month": ec.getMonth(),
            "day": day_gz,
            "hour": hour_gz,
        },
        hour_zhi=ec.getTimeZhi(),
        true_solar_time=dt.strftime("%Y-%m-%d %H:%M:%S"),
        civil_time=civil,
    )
