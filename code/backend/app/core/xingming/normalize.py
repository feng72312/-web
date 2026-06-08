from __future__ import annotations

from typing import Any

from app.core.tianxiang.mansions import MANSION_TABLE_VERSION
from app.core.tianxiang.si_yu import SI_YU_MODEL
from app.core.xingming.calendar_bridge import XingmingCalendarContext
from app.core.xingming.limits import build_limits, is_day_chart
from app.core.xingming.models import XingmingInput
from app.core.xingming.palaces import assign_stars_to_palaces, build_palace_grid
from app.core.xingming.rules import XingmingRules


def normalize_chart(
    ctx: XingmingCalendarContext,
    data: XingmingInput,
    rules: XingmingRules,
    bodies: list[dict[str, Any]],
    ascendant: float,
    target_year: int,
) -> dict[str, Any]:
    palaces = build_palace_grid(ascendant)
    assign_stars_to_palaces(palaces, bodies, ascendant)
    sun_lon = next((b["longitude"] for b in bodies if b["id"] == "sun"), 0.0)
    day_chart = is_day_chart(sun_lon, ascendant)
    if rules.day_night_rule == "day":
        day_chart = True
    elif rules.day_night_rule == "night":
        day_chart = False

    ming = palaces[0]
    return {
        "input": data.to_dict(),
        "trueSolarTime": ctx.true_solar_time,
        "fourPillars": ctx.four_pillars,
        "meta": {
            "engine": "xingming",
            "school": rules.school,
            "version": 1,
            "isDay": day_chart,
            "genderLabel": ctx.gender_label,
        },
        "rulesMeta": {
            "mansionTableVersion": MANSION_TABLE_VERSION,
            "siYuModel": SI_YU_MODEL,
            "rulesApplied": ctx.rules_applied,
            "ascendantLongitude": round(ascendant, 4),
        },
        "bodies": bodies,
        "palaces": palaces,
        "limits": build_limits(ascendant, target_year),
        "crossRef": {
            "baziDayMaster": None,
            "ziweiSoulPalace": None,
        },
        "mingPalace": {
            "name": ming["name"],
            "branch": ming["branch"],
            "majorStars": ming["majorStars"],
        },
    }
