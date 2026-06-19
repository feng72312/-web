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

DEFAULT_TOPICS = ("tiaohou", "shishen", "ganzhi", "dayun", "liunian", "geju", "qishi")


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


SEASON_ZHI_ORDER: dict[str, tuple[str, ...]] = {
    "spring": ("寅", "卯", "辰"),
    "summer": ("巳", "午", "未"),
    "autumn": ("申", "酉", "戌"),
    "winter": ("亥", "子", "丑"),
}


def season_sibling_zhis(month_zhi: str) -> list[str]:
    """Same-season month branches for tiaohou fallback when exact month node is missing."""
    for zhis in SEASON_ZHI_ORDER.values():
        if month_zhi in zhis:
            return [z for z in zhis if z != month_zhi]
    return []


def build_tiaohou_fallback_keys(day_gan: str, month_zhi: str) -> list[dict[str, str]]:
    keys: list[dict[str, str]] = []
    for zhi in season_sibling_zhis(month_zhi):
        keys.append(
            {
                "dayGan": day_gan,
                "monthZhi": zhi,
                "monthLabel": ZHI_TO_MONTH_LABEL.get(zhi, ""),
            }
        )
    return keys


GEJU_ALIASES: dict[str, str] = {
    "偏财": "正财",
    "偏印": "正印",
    "劫财": "比肩",
}


def normalize_geju_name(month_shishen: str) -> str:
    return GEJU_ALIASES.get(month_shishen, month_shishen)


def build_geju_key(chart: dict[str, Any]) -> dict[str, str]:
    pillars = chart.get("pillars") or {}
    month_ss = pillars.get("month", {}).get("shishenGan") or ""
    month_zhi = pillars.get("month", {}).get("zhi") or ""
    if not month_ss:
        raise ValueError("chart missing month shishen")
    geju_name = normalize_geju_name(month_ss)
    return {
        "monthShishen": geju_name,
        "monthZhi": month_zhi,
        "gejuName": geju_name,
        "aspect": "core",
    }


def build_geju_aspect_key(aspect: str) -> dict[str, str]:
    return {"aspect": aspect, "category": "geju_outcome"}


def build_geju_special_key(pattern: str) -> dict[str, str]:
    return {"pattern": pattern, "category": "geju_special"}


def build_qishi_key(chart: dict[str, Any]) -> dict[str, str]:
    wx = chart.get("wuxingCount") or {}
    if not wx:
        raise ValueError("chart missing wuxingCount")
    dominant = max(wx, key=wx.get)
    weakest = min(wx, key=wx.get)
    return {
        "dominant": dominant,
        "weakest": weakest,
        "category": "wuxing_bias",
    }


def build_shishen_key(chart: dict[str, Any]) -> dict[str, str]:
    keys = build_shishen_lookup_keys(chart)
    if not keys:
        raise ValueError("chart missing shishen lookup keys")
    return keys[0]


from app.core.knowledge.shishen_context import build_shishen_lookup_keys
from app.core.knowledge.keys_interactions import build_interaction_keys
from app.core.knowledge.luck_chart import resolve_active_dayun, resolve_target_year


def build_suiyun_key(chart: dict[str, Any]) -> dict[str, str]:
    active = resolve_active_dayun(chart, resolve_target_year(chart))
    ganzhi = str((active or {}).get("ganzhi") or "")
    if not ganzhi:
        dayun = chart.get("dayun") or []
        if not dayun:
            raise ValueError("chart missing dayun")
        ganzhi = str(dayun[0].get("ganzhi") or "")
    if not ganzhi:
        raise ValueError("chart missing dayun ganzhi")
    return {
        "ganzhi": ganzhi,
        "category": "ganzhi_dayun",
    }


def build_chart_lookup_keys(chart: dict[str, Any]) -> dict[str, dict[str, str]]:
    keys: dict[str, dict[str, str]] = {}
    try:
        keys["tiaohou"] = build_tiaohou_key(chart)
    except ValueError:
        pass
    try:
        keys["geju"] = build_geju_key(chart)
    except ValueError:
        pass
    try:
        keys["qishi"] = build_qishi_key(chart)
    except ValueError:
        pass
    try:
        keys["shishen"] = build_shishen_key(chart)
    except ValueError:
        pass
    try:
        keys["suiyun"] = build_suiyun_key(chart)
    except ValueError:
        pass
    interaction_keys = build_interaction_keys(chart)
    if interaction_keys:
        keys["interactions"] = interaction_keys
    return keys
