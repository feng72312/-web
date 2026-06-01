from __future__ import annotations

from typing import Any

ZHI_TO_MONTH_LABEL: dict[str, str] = {
    "寅": "正月",
    "卯": "二月",
    "辰": "三月",
    "巳": "四月",
    "午": "五月",
    "未": "六月",
    "申": "七月",
    "酉": "八月",
    "戌": "九月",
    "亥": "十月",
    "子": "十一月",
    "丑": "十二月",
}

MONTH_LABEL_TO_ZHI = {value: key for key, value in ZHI_TO_MONTH_LABEL.items()}

DEFAULT_TOPICS = ("tiaohou", "shishen", "ganzhi", "dayun", "liunian")


def entry_id_for_tiaohou(day_gan: str, month_zhi: str) -> str:
    return f"tiaohou:{day_gan}:{month_zhi}"


def build_tiaohou_key(chart: dict[str, Any]) -> dict[str, str]:
    pillars = chart.get("pillars") or {}
    day_gan = pillars.get("day", {}).get("gan") or chart.get("dayMaster") or ""
    month_zhi = pillars.get("month", {}).get("zhi") or ""
    if not day_gan or not month_zhi:
        raise ValueError("chart missing day gan or month zhi")
    return {
        "dayGan": day_gan,
        "monthZhi": month_zhi,
        "monthLabel": ZHI_TO_MONTH_LABEL.get(month_zhi, ""),
    }


def build_chart_lookup_keys(chart: dict[str, Any]) -> dict[str, dict[str, str]]:
    keys: dict[str, dict[str, str]] = {}
    try:
        keys["tiaohou"] = build_tiaohou_key(chart)
    except ValueError:
        pass
    return keys
