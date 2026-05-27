from __future__ import annotations

from lunar_python import Lunar, Solar

from app.core.liuyao.models import LiuyaoInput

ZHI_NUM = {
    "子": 1,
    "丑": 2,
    "寅": 3,
    "卯": 4,
    "辰": 5,
    "巳": 6,
    "午": 7,
    "未": 8,
    "申": 9,
    "酉": 10,
    "戌": 11,
    "亥": 12,
}


def resolve_calendar_context(data: LiuyaoInput) -> dict:
    if data.calendar_type == "lunar":
        lunar = Lunar.fromYmdHms(
            data.year,
            data.month,
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

    ec = lunar.getEightChar()
    ec.setSect(2)
    year_zhi = ec.getYearZhi()
    hour_zhi = ec.getTimeZhi()
    year_zhi_num = ZHI_NUM[year_zhi]
    hour_zhi_num = ZHI_NUM[hour_zhi]
    lunar_month = lunar.getMonth()
    lunar_day = lunar.getDay()

    base = year_zhi_num + lunar_month + lunar_day
    upper_num = base
    lower_num = base + hour_zhi_num
    moving_num = base + hour_zhi_num

    return {
        "solar": solar.toYmdHms(),
        "lunar": lunar.toString(),
        "year_zhi": year_zhi,
        "hour_zhi": hour_zhi,
        "year_zhi_num": year_zhi_num,
        "hour_zhi_num": hour_zhi_num,
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
        "month_jian": ec.getMonthZhi(),
        "day_gan": ec.getDayGan(),
        "day_chen": ec.getDayZhi(),
        "upper_num": upper_num,
        "lower_num": lower_num,
        "moving_num": moving_num,
    }


def calendar_for_chart(data: LiuyaoInput) -> dict[str, str]:
    ctx = resolve_calendar_context(data)
    return {
        "monthJian": ctx["month_jian"],
        "dayChen": ctx["day_chen"],
        "dayGan": ctx["day_gan"],
    }
