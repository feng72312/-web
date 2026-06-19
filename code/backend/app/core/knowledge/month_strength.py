"""Rule-derived month-command strength assessment for MonthStrengthJudge."""

from __future__ import annotations

from typing import Any

SEASON_BY_ZHI: dict[str, str] = {
    "寅": "spring",
    "卯": "spring",
    "辰": "spring",
    "巳": "summer",
    "午": "summer",
    "未": "summer",
    "申": "autumn",
    "酉": "autumn",
    "戌": "autumn",
    "亥": "winter",
    "子": "winter",
    "丑": "winter",
}

SEASON_ORDER: dict[str, tuple[str, ...]] = {
    "spring": ("木", "火", "水", "金", "土"),
    "summer": ("火", "土", "木", "水", "金"),
    "autumn": ("金", "水", "土", "火", "木"),
    "winter": ("水", "木", "金", "土", "火"),
}

SLOT_LABELS = ("旺", "相", "休", "囚", "死")

RESOURCE_SHISHEN = frozenset({"正印", "偏印", "比肩", "劫财"})
DRAIN_SHISHEN = frozenset({"食神", "伤官"})


def _month_zhi(chart: dict[str, Any]) -> str:
    return str((chart.get("pillars") or {}).get("month", {}).get("zhi") or "")


def _day_wuxing(chart: dict[str, Any]) -> str:
    return str(chart.get("dayMasterWuxing") or "")


def season_slot(month_zhi: str, day_wuxing: str) -> str:
    season = SEASON_BY_ZHI.get(month_zhi, "")
    order = SEASON_ORDER.get(season)
    if not order or day_wuxing not in order:
        return "休"
    return SLOT_LABELS[order.index(day_wuxing)]


def _count_shishen_roles(chart: dict[str, Any]) -> tuple[int, int]:
    support = 0
    drain = 0
    pillars = chart.get("pillars") or {}
    for key in ("year", "month", "day", "hour"):
        ss = str(pillars.get(key, {}).get("shishenGan") or "")
        if ss in RESOURCE_SHISHEN:
            support += 1
        elif ss in DRAIN_SHISHEN:
            drain += 1
    return support, drain


def assess_month_strength(chart: dict[str, Any]) -> dict[str, Any]:
    month_zhi = _month_zhi(chart)
    day_wx = _day_wuxing(chart)
    slot = season_slot(month_zhi, day_wx)
    wx_count = chart.get("wuxingCount") or {}
    self_count = int(wx_count.get(day_wx, 0) or 0)
    support, drain = _count_shishen_roles(chart)

    if slot in ("旺", "相"):
        if self_count >= 3 or support >= 2:
            body = "身强"
            stance = "favorable"
        else:
            body = "得令而根气未足"
            stance = "conditional"
    elif slot == "休":
        if support >= 2 and drain <= 1:
            body = "中和偏弱"
            stance = "conditional"
        else:
            body = "身弱"
            stance = "unfavorable"
    else:
        if support >= 2:
            body = "失令有印比扶助"
            stance = "conditional"
        else:
            body = "失令身弱"
            stance = "unfavorable"

    summary = (
        f"月支{month_zhi}日主{day_wx}当令{slot}, {body}; "
        f"五行同类{self_count}, 印比透干{support}, 食伤泄气{drain}"
    )
    boundary = "旺衰须与格局体用、调候寒暖并列, 不可单以得令失令定吉凶"
    return {
        "summary": summary,
        "slot": slot,
        "body": body,
        "stance": stance,
        "boundary": boundary,
        "ruleIds": [f"month:strength:{slot}"],
    }
