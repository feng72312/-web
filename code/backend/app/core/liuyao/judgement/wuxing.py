from __future__ import annotations

from app.core.liuyao.najia import BRANCH_ELEMENT, CONTROLS, GENERATES

GAN_ORDER = "甲乙丙丁戊己庚辛壬癸"
ZHI_ORDER = "子丑寅卯辰巳午未申酉戌亥"

ZHI_CLASH: dict[str, str] = {
    "子": "午",
    "午": "子",
    "丑": "未",
    "未": "丑",
    "寅": "申",
    "申": "寅",
    "卯": "酉",
    "酉": "卯",
    "辰": "戌",
    "戌": "辰",
    "巳": "亥",
    "亥": "巳",
}

XUN_KONG_BY_GANZHI: dict[str, tuple[str, str]] = {}
for _i in range(60):
    _gan = GAN_ORDER[_i % 10]
    _zhi = ZHI_ORDER[_i % 12]
    _pair = (
        ("戌", "亥"),
        ("申", "酉"),
        ("午", "未"),
        ("辰", "巳"),
        ("寅", "卯"),
        ("子", "丑"),
    )[_i // 10]
    XUN_KONG_BY_GANZHI[_gan + _zhi] = _pair

CLASH_TRIGRAM: dict[str, str] = {
    "乾": "坤",
    "坤": "乾",
    "坎": "离",
    "离": "坎",
    "震": "兑",
    "兑": "震",
    "艮": "巽",
    "巽": "艮",
}

LIU_CHONG_EXTRA = {
    "天雷无妄",
    "风地观",
    "雷山小过",
    "泽风大过",
    "山泽损",
}


def branch_element(branch: str) -> str:
    return BRANCH_ELEMENT.get(branch, "")


def element_relation(source: str, target: str) -> str:
    if not source or not target:
        return "neutral"
    if source == target:
        return "same"
    if GENERATES.get(source) == target:
        return "generates"
    if GENERATES.get(target) == source:
        return "generated_by"
    if CONTROLS.get(source) == target:
        return "controls"
    if CONTROLS.get(target) == source:
        return "controlled_by"
    return "neutral"


def xun_kong_branches(day_gan: str, day_chen: str) -> tuple[str, str]:
    return XUN_KONG_BY_GANZHI.get(day_gan + day_chen, ("", ""))


def is_yue_po(branch: str, month_jian: str) -> bool:
    return ZHI_CLASH.get(branch, "") == month_jian


def is_in_xun_kong(branch: str, day_gan: str, day_chen: str) -> bool:
    empty = xun_kong_branches(day_gan, day_chen)
    return branch in empty


def is_liu_chong_hexagram(lower: str, upper: str, name: str = "") -> bool:
    if CLASH_TRIGRAM.get(lower) == upper:
        return True
    return name in LIU_CHONG_EXTRA
