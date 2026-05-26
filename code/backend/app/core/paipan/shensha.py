from __future__ import annotations

PILLAR_KEYS = ("year", "month", "day", "hour")

TIAN_YI: dict[str, list[str]] = {
    "\u7532": ["\u4e11", "\u672a"],
    "\u620a": ["\u4e11", "\u672a"],
    "\u5e9a": ["\u4e11", "\u672a"],
    "\u4e59": ["\u5b50", "\u7533"],
    "\u5df1": ["\u5b50", "\u7533"],
    "\u4e19": ["\u4ea5", "\u9149"],
    "\u4e01": ["\u4ea5", "\u9149"],
    "\u58ec": ["\u5df3", "\u536f"],
    "\u7678": ["\u5df3", "\u536f"],
}

WEN_CHANG: dict[str, str] = {
    "\u7532": "\u5df3",
    "\u4e59": "\u5348",
    "\u4e19": "\u7533",
    "\u4e01": "\u9149",
    "\u620a": "\u7533",
    "\u5df1": "\u9149",
    "\u5e9a": "\u4ea5",
    "\u8f9b": "\u5b50",
    "\u58ec": "\u7533",
    "\u7678": "\u9149",
}

YI_MA_GROUPS = [
    (("\u7533", "\u5b50", "\u8fb0"), "\u5bc5"),
    (("\u5bc5", "\u5348", "\u620c"), "\u7533"),
    (("\u5df3", "\u9149", "\u4e11"), "\u4ea5"),
    (("\u4ea5", "\u536f", "\u672a"), "\u5df3"),
]

TAO_HUA_GROUPS = [
    (("\u7533", "\u5b50", "\u8fb0"), "\u536f"),
    (("\u5bc5", "\u5348", "\u620c"), "\u9149"),
    (("\u5df3", "\u9149", "\u4e11"), "\u5348"),
    (("\u4ea5", "\u536f", "\u672a"), "\u5b50"),
]


def _group_target(zhi: str, groups: list) -> str:
    for members, target in groups:
        if zhi in members:
            return target
    return ""


def pillar_shen_sha(day_gan: str, year_zhi: str, pillar_gan: str, pillar_zhi: str) -> list[str]:
    stars: list[str] = []
    if pillar_zhi in TIAN_YI.get(day_gan, []):
        stars.append("\u5929\u4e59\u8d35\u4eba")
    if WEN_CHANG.get(day_gan) == pillar_zhi:
        stars.append("\u6587\u660e\u8d35\u4eba")
    if _group_target(year_zhi, YI_MA_GROUPS) == pillar_zhi:
        stars.append("\u9a7e\u9a6c")
    if _group_target(year_zhi, TAO_HUA_GROUPS) == pillar_zhi:
        stars.append("\u6843\u82b1")
    return stars
