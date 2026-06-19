from __future__ import annotations

from collections import Counter
from typing import Any

from app.core.utils.naming_engine import favored_wuxing_from_chart

BOUNDARY_PATTERNS = ("zagai", "waige", "jishen_po", "xionshen_cheng")

GAN_HE_PAIRS = (
    frozenset({"甲", "己"}),
    frozenset({"乙", "庚"}),
    frozenset({"丙", "辛"}),
    frozenset({"丁", "壬"}),
    frozenset({"戊", "癸"}),
)

ZHI_CHONG = (
    frozenset({"子", "午"}),
    frozenset({"丑", "未"}),
    frozenset({"寅", "申"}),
    frozenset({"卯", "酉"}),
    frozenset({"辰", "戌"}),
    frozenset({"巳", "亥"}),
)

DAY_GAN_LU: dict[str, str] = {
    "甲": "寅",
    "乙": "卯",
    "丙": "巳",
    "丁": "午",
    "戊": "巳",
    "己": "午",
    "庚": "申",
    "辛": "酉",
    "壬": "亥",
    "癸": "子",
}

WINTER_ZHI = frozenset({"亥", "子", "丑"})
WATER_FRAME = frozenset({"申", "子", "辰"})
YIN_SI_SHEN_XING = frozenset({"寅", "巳", "申"})
CHOU_XU_WEI_XING = frozenset({"丑", "戌", "未"})

WEALTH_STARS = frozenset({"正财", "偏财"})
OFFICER_STARS = frozenset({"正官", "七杀"})


def _pillar_keys(chart: dict[str, Any]) -> list[str]:
    pillars = chart.get("pillars") or {}
    return [key for key in ("year", "month", "day", "hour") if key in pillars]


def collect_shishen_counts(chart: dict[str, Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for key in _pillar_keys(chart):
        pillar = chart["pillars"][key]
        gan_ss = str(pillar.get("shishenGan") or "").strip()
        if gan_ss:
            counts[gan_ss] += 1
        for zhi_ss in pillar.get("shishenZhi") or []:
            label = str(zhi_ss or "").strip()
            if label:
                counts[label] += 1
    return counts


def _collect_gans(chart: dict[str, Any]) -> list[str]:
    gans: list[str] = []
    for key in _pillar_keys(chart):
        gan = str(chart["pillars"][key].get("gan") or "").strip()
        if gan:
            gans.append(gan)
    return gans


def _collect_zhis(chart: dict[str, Any]) -> list[str]:
    zhis: list[str] = []
    for key in _pillar_keys(chart):
        zhi = str(chart["pillars"][key].get("zhi") or "").strip()
        if zhi:
            zhis.append(zhi)
    return zhis


def _has_gan_he(gans: list[str]) -> bool:
    for idx, left in enumerate(gans):
        for right in gans[idx + 1 :]:
            if frozenset({left, right}) in GAN_HE_PAIRS:
                return True
    return False


def _has_zhi_chong(zhis: list[str]) -> bool:
    zhi_set = set(zhis)
    for pair in ZHI_CHONG:
        if pair.issubset(zhi_set):
            return True
    return False


def _has_san_xing(zhis: list[str], group: frozenset[str]) -> bool:
    hits = sum(1 for zhi in zhis if zhi in group)
    return hits >= 2


def _has_yao_he(gans: list[str]) -> bool:
    if len(gans) < 2:
        return False
    year_gan = gans[0]
    hour_gan = gans[-1]
    return frozenset({year_gan, hour_gan}) in GAN_HE_PAIRS and year_gan != hour_gan


from app.core.paipan.wuxing_map import gan_wuxing


def _day_master_root_score(chart: dict[str, Any]) -> float:
    day_gan = str(
        chart.get("dayMaster")
        or (chart.get("pillars") or {}).get("day", {}).get("gan")
        or ""
    )
    if not day_gan:
        return 0.0
    dm_wx = str(chart.get("dayMasterWuxing") or gan_wuxing(day_gan))
    score = 0.0
    for key in _pillar_keys(chart):
        pillar = chart["pillars"][key]
        if key != "day":
            gan = str(pillar.get("gan") or "").strip()
            if gan == day_gan:
                score += 1.0
            elif gan and gan_wuxing(gan) == dm_wx:
                score += 0.5
        for hide in pillar.get("hideGan") or []:
            hide_gan = str(hide or "").strip()
            if not hide_gan:
                continue
            if hide_gan == day_gan:
                score += 0.8
            elif gan_wuxing(hide_gan) == dm_wx:
                score += 0.4
    return score


def detect_geju_special_patterns(chart: dict[str, Any]) -> list[str]:
    """Return geju special pattern keys to attach as ruleIds."""
    patterns: list[str] = list(BOUNDARY_PATTERNS)

    wx = chart.get("wuxingCount") or {}
    dm_wx = str(chart.get("dayMasterWuxing") or "")
    day_gan = str(chart.get("dayMaster") or (chart.get("pillars") or {}).get("day", {}).get("gan") or "")
    gans = _collect_gans(chart)
    zhis = _collect_zhis(chart)
    zhi_set = set(zhis)
    ss_counts = collect_shishen_counts(chart)

    if wx:
        total = sum(wx.values()) or 1
        dominant = max(wx, key=wx.get)
        dominant_ratio = wx[dominant] / total
        dm_ratio = wx.get(dm_wx, 0) / total if dm_wx else 0.0
        if dm_wx and dm_ratio >= 0.45:
            patterns.append("zhuanwang")
        elif dominant_ratio >= 0.42:
            patterns.append("quzhi")

    try:
        profile = favored_wuxing_from_chart(chart)
        strength = str(profile.get("strength") or "")
    except Exception:
        strength = ""

    wealth_count = sum(ss_counts[star] for star in WEALTH_STARS)
    officer_count = sum(ss_counts[star] for star in OFFICER_STARS)
    root_score = _day_master_root_score(chart)

    if strength == "偏弱" and root_score < 1.0:
        if wealth_count >= 2:
            patterns.append("congcai")
        if officer_count >= 2:
            patterns.append("congsha")

    if _has_gan_he(gans):
        patterns.append("huaji")
    if _has_zhi_chong(zhis):
        patterns.append("daochong")

    month_zhi = str((chart.get("pillars") or {}).get("month", {}).get("zhi") or "")
    if day_gan in {"丙", "丁"} and month_zhi in WINTER_ZHI:
        patterns.append("chaoyang")

    lu_zhi = DAY_GAN_LU.get(day_gan, "")
    if lu_zhi and lu_zhi in zhi_set:
        patterns.append("helu")

    if "子" in zhi_set and len(zhi_set & WATER_FRAME) >= 2:
        patterns.append("jinglan")
    if _has_san_xing(zhis, YIN_SI_SHEN_XING) or _has_san_xing(zhis, CHOU_XU_WEI_XING):
        patterns.append("xinghe")
    if _has_yao_he(gans):
        patterns.append("yaohe")

    deduped: list[str] = []
    seen: set[str] = set()
    for pattern in patterns:
        if pattern not in seen:
            seen.add(pattern)
            deduped.append(pattern)
    return deduped
