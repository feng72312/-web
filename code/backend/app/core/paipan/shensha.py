from __future__ import annotations

from dataclasses import dataclass

ZHI_ORDER = (
    "\u5b50",
    "\u4e11",
    "\u5bc5",
    "\u536f",
    "\u8fb0",
    "\u5df3",
    "\u5348",
    "\u672a",
    "\u7533",
    "\u9149",
    "\u620c",
    "\u4ea5",
)

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

TAI_JI: dict[str, list[str]] = {
    "\u7532": ["\u5b50", "\u5348"],
    "\u4e59": ["\u5b50", "\u5348"],
    "\u4e19": ["\u536f", "\u9149"],
    "\u4e01": ["\u536f", "\u9149"],
    "\u58ec": ["\u4ea5", "\u7533"],
    "\u7678": ["\u4ea5", "\u7533"],
    "\u620a": ["\u7533", "\u5b50"],
    "\u5df1": ["\u7533", "\u5b50"],
    "\u5e9a": ["\u4e11", "\u672a"],
    "\u8f9b": ["\u4e11", "\u672a"],
}

GUO_YIN: dict[str, str] = {
    "\u7532": "\u620c",
    "\u4e59": "\u4ea5",
    "\u4e19": "\u4e11",
    "\u4e01": "\u5bc5",
    "\u620a": "\u4e11",
    "\u5df1": "\u5bc5",
    "\u5e9a": "\u8fb0",
    "\u8f9b": "\u5df3",
    "\u58ec": "\u672a",
    "\u7678": "\u7533",
}

JIN_YU: dict[str, str] = {
    "\u7532": "\u8fb0",
    "\u4e59": "\u5df3",
    "\u4e19": "\u672a",
    "\u4e01": "\u7533",
    "\u620a": "\u672a",
    "\u5df1": "\u7533",
    "\u5e9a": "\u620c",
    "\u8f9b": "\u4ea5",
    "\u58ec": "\u4e11",
    "\u7678": "\u5bc5",
}

TIAN_CHU: dict[str, str] = {
    "\u7532": "\u5df3",
    "\u4e59": "\u5348",
    "\u4e19": "\u5df3",
    "\u4e01": "\u5348",
    "\u620a": "\u7533",
    "\u5df1": "\u9149",
    "\u5e9a": "\u4ea5",
    "\u8f9b": "\u5b50",
    "\u58ec": "\u5bc5",
    "\u7678": "\u536f",
}

XUE_TANG: dict[str, str] = {
    "\u7532": "\u4ea5",
    "\u4e59": "\u5348",
    "\u4e19": "\u5bc5",
    "\u4e01": "\u9149",
    "\u620a": "\u5bc5",
    "\u5df1": "\u9149",
    "\u5e9a": "\u5df3",
    "\u8f9b": "\u5b50",
    "\u58ec": "\u8fb0",
    "\u7678": "\u536f",
}

CI_GUAN: dict[str, str] = {
    "\u7532": "\u5bc5",
    "\u4e59": "\u536f",
    "\u4e19": "\u5df3",
    "\u4e01": "\u5348",
    "\u620a": "\u5df3",
    "\u5df1": "\u5348",
    "\u5e9a": "\u7533",
    "\u8f9b": "\u9149",
    "\u58ec": "\u4ea5",
    "\u7678": "\u5b50",
}

LU_SHEN: dict[str, str] = {
    "\u7532": "\u5bc5",
    "\u4e59": "\u536f",
    "\u4e19": "\u5df3",
    "\u4e01": "\u5348",
    "\u620a": "\u5df3",
    "\u5df1": "\u5348",
    "\u5e9a": "\u7533",
    "\u8f9b": "\u9149",
    "\u58ec": "\u4ea5",
    "\u7678": "\u5b50",
}

YANG_REN: dict[str, str] = {
    "\u7532": "\u536f",
    "\u4e59": "\u8fb0",
    "\u4e19": "\u5348",
    "\u4e01": "\u672a",
    "\u620a": "\u5348",
    "\u5df1": "\u672a",
    "\u5e9a": "\u9149",
    "\u8f9b": "\u620c",
    "\u58ec": "\u5b50",
    "\u7678": "\u4e11",
}

FEI_REN: dict[str, str] = {
    "\u7532": "\u9149",
    "\u4e59": "\u620c",
    "\u4e19": "\u5b50",
    "\u4e01": "\u4e11",
    "\u620a": "\u5b50",
    "\u5df1": "\u4e11",
    "\u5e9a": "\u536f",
    "\u8f9b": "\u8fb0",
    "\u58ec": "\u5348",
    "\u7678": "\u672a",
}

XUE_REN: dict[str, str] = {
    "\u7532": "\u536f",
    "\u4e59": "\u8fb0",
    "\u4e19": "\u5348",
    "\u4e01": "\u672a",
    "\u620a": "\u5348",
    "\u5df1": "\u672a",
    "\u5e9a": "\u9149",
    "\u8f9b": "\u620c",
    "\u58ec": "\u5b50",
    "\u7678": "\u4e11",
}

HONG_YAN: dict[str, str] = {
    "\u7532": "\u5348",
    "\u4e59": "\u7533",
    "\u4e19": "\u5bc5",
    "\u4e01": "\u672a",
    "\u620a": "\u8fb0",
    "\u5df1": "\u8fb0",
    "\u5e9a": "\u620c",
    "\u8f9b": "\u9149",
    "\u58ec": "\u5b50",
    "\u7678": "\u7533",
}

TIAN_DE: dict[str, str] = {
    "\u5bc5": "\u4e01",
    "\u536f": "\u7533",
    "\u8fb0": "\u58ec",
    "\u5df3": "\u8f9b",
    "\u5348": "\u4ea5",
    "\u672a": "\u7532",
    "\u7533": "\u7678",
    "\u9149": "\u5bc5",
    "\u620c": "\u4e19",
    "\u4ea5": "\u4e59",
    "\u5b50": "\u5df3",
    "\u4e11": "\u5e9a",
}

YUE_DE: dict[str, tuple[str, ...]] = {
    "\u5bc5": ("\u4e19",),
    "\u5348": ("\u4e19",),
    "\u620c": ("\u4e19",),
    "\u7533": ("\u58ec",),
    "\u5b50": ("\u58ec",),
    "\u8fb0": ("\u58ec",),
    "\u5df3": ("\u5e9a",),
    "\u9149": ("\u5e9a",),
    "\u4e11": ("\u5e9a",),
    "\u4ea5": ("\u7532",),
    "\u536f": ("\u7532",),
    "\u672a": ("\u7532",),
}

TIAN_YI_MONTH: dict[str, str] = {
    "\u5bc5": "\u4e11",
    "\u536f": "\u4ea5",
    "\u8fb0": "\u620c",
    "\u5df3": "\u5b50",
    "\u5348": "\u4ea5",
    "\u672a": "\u7533",
    "\u7533": "\u4e11",
    "\u9149": "\u5b50",
    "\u620c": "\u4ea5",
    "\u4ea5": "\u7533",
    "\u5b50": "\u4e11",
    "\u4e11": "\u5b50",
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

HUA_GAI_GROUPS = [
    (("\u5bc5", "\u5348", "\u620c"), "\u620c"),
    (("\u7533", "\u5b50", "\u8fb0"), "\u620c"),
    (("\u5df3", "\u9149", "\u4e11"), "\u4e11"),
    (("\u4ea5", "\u536f", "\u672a"), "\u672a"),
]

JIE_SHA_GROUPS = [
    (("\u5bc5", "\u5348", "\u620c"), "\u4ea5"),
    (("\u7533", "\u5b50", "\u8fb0"), "\u4ea5"),
    (("\u5df3", "\u9149", "\u4e11"), "\u5bc5"),
    (("\u4ea5", "\u536f", "\u672a"), "\u7533"),
]

WANG_SHEN_GROUPS = [
    (("\u5bc5", "\u5348", "\u620c"), "\u5df3"),
    (("\u7533", "\u5b50", "\u8fb0"), "\u5df3"),
    (("\u5df3", "\u9149", "\u4e11"), "\u7533"),
    (("\u4ea5", "\u536f", "\u672a"), "\u5bc5"),
]

ZAI_SHA_GROUPS = [
    (("\u5bc5", "\u5348", "\u620c"), "\u5b50"),
    (("\u7533", "\u5b50", "\u8fb0"), "\u5b50"),
    (("\u5df3", "\u9149", "\u4e11"), "\u536f"),
    (("\u4ea5", "\u536f", "\u672a"), "\u9149"),
]

JIANG_XING_GROUPS = [
    (("\u5bc5", "\u5348", "\u620c"), "\u5348"),
    (("\u7533", "\u5b50", "\u8fb0"), "\u5b50"),
    (("\u5df3", "\u9149", "\u4e11"), "\u9149"),
    (("\u4ea5", "\u536f", "\u672a"), "\u536f"),
]

GUCHEN_GROUPS = [
    (("\u5bc5", "\u536f", "\u8fb0"), "\u5df3"),
    (("\u5df3", "\u5348", "\u672a"), "\u7533"),
    (("\u7533", "\u9149", "\u620c"), "\u4ea5"),
    (("\u4ea5", "\u5b50", "\u4e11"), "\u5bc5"),
]

GUAXIU_GROUPS = [
    (("\u5bc5", "\u536f", "\u8fb0"), "\u4e11"),
    (("\u5df3", "\u5348", "\u672a"), "\u8fb0"),
    (("\u7533", "\u9149", "\u620c"), "\u672a"),
    (("\u4ea5", "\u5b50", "\u4e11"), "\u620c"),
]

HONG_LUAN: dict[str, str] = {
    "\u5b50": "\u536f",
    "\u4e11": "\u5bc5",
    "\u5bc5": "\u4e11",
    "\u536f": "\u5b50",
    "\u8fb0": "\u4ea5",
    "\u5df3": "\u620c",
    "\u5348": "\u9149",
    "\u672a": "\u7533",
    "\u7533": "\u672a",
    "\u9149": "\u5348",
    "\u620c": "\u5df3",
    "\u4ea5": "\u8fb0",
}

TIAN_XI: dict[str, str] = {
    "\u5b50": "\u9149",
    "\u4e11": "\u7533",
    "\u5bc5": "\u672a",
    "\u536f": "\u5b50",
    "\u8fb0": "\u5df3",
    "\u5df3": "\u8fb0",
    "\u5348": "\u536f",
    "\u672a": "\u5bc5",
    "\u7533": "\u4e11",
    "\u9149": "\u5b50",
    "\u620c": "\u4ea5",
    "\u4ea5": "\u5348",
}

YUAN_CHEN_FORWARD: dict[str, str] = {
    "\u5b50": "\u672a",
    "\u4e11": "\u7533",
    "\u5bc5": "\u9149",
    "\u536f": "\u620c",
    "\u8fb0": "\u4ea5",
    "\u5df3": "\u5b50",
    "\u5348": "\u4e11",
    "\u672a": "\u5bc5",
    "\u7533": "\u8fb0",
    "\u9149": "\u5df3",
    "\u620c": "\u5348",
    "\u4ea5": "\u7533",
}

YUAN_CHEN_REVERSE: dict[str, str] = {
    "\u5b50": "\u5df3",
    "\u4e11": "\u5348",
    "\u5bc5": "\u536f",
    "\u536f": "\u4e11",
    "\u8fb0": "\u5b50",
    "\u5df3": "\u4ea5",
    "\u5348": "\u672a",
    "\u672a": "\u7533",
    "\u7533": "\u8fb0",
    "\u9149": "\u620c",
    "\u620c": "\u4e11",
    "\u4ea5": "\u5b50",
}

KUI_GANG = frozenset({"\u5e9a\u8fb0", "\u5e9a\u620c", "\u58ec\u8fb0", "\u620a\u620c"})
RI_DE = frozenset({"\u7532\u5bc5", "\u4e19\u8fb0", "\u620a\u8fb0", "\u5e9a\u8fb0", "\u58ec\u620c"})
RI_GUI = frozenset(
    {
        "\u4e01\u9149",
        "\u4e01\u4ea5",
        "\u7678\u536f",
        "\u7678\u5df3",
        "\u4e59\u5df3",
        "\u4e59\u536f",
        "\u4e19\u5bc5",
        "\u7532\u5b50",
    }
)
JIN_SHEN = frozenset({"\u4e59\u4e11", "\u5df1\u5df3", "\u7678\u9149"})
TIAN_SHE = frozenset({"\u620a\u5bc5", "\u7532\u5348", "\u620a\u7533", "\u7532\u5b50"})


@dataclass(frozen=True)
class ShenShaContext:
    day_gan: str
    day_zhi: str
    year_gan: str
    year_zhi: str
    month_zhi: str
    gender: int = 1


def _group_target(zhi: str, groups: list) -> str:
    for members, target in groups:
        if zhi in members:
            return target
    return ""


def _offset_zhi(base: str, offset: int) -> str:
    if base not in ZHI_ORDER:
        return ""
    idx = ZHI_ORDER.index(base)
    return ZHI_ORDER[(idx + offset) % 12]


def _append(stars: list[str], name: str, matched: bool) -> None:
    if matched and name not in stars:
        stars.append(name)


def make_shen_sha_context(
    *,
    day_gan: str,
    day_zhi: str,
    year_gan: str,
    year_zhi: str,
    month_zhi: str,
    gender: int = 1,
) -> ShenShaContext:
    return ShenShaContext(
        day_gan=day_gan,
        day_zhi=day_zhi,
        year_gan=year_gan,
        year_zhi=year_zhi,
        month_zhi=month_zhi,
        gender=gender,
    )


def pillar_shen_sha(
    day_gan: str,
    year_zhi: str,
    pillar_gan: str,
    pillar_zhi: str,
    *,
    day_zhi: str = "",
    year_gan: str = "",
    month_zhi: str = "",
    gender: int = 1,
) -> list[str]:
    ctx = make_shen_sha_context(
        day_gan=day_gan,
        day_zhi=day_zhi,
        year_gan=year_gan,
        year_zhi=year_zhi,
        month_zhi=month_zhi,
        gender=gender,
    )
    return collect_pillar_shen_sha(ctx, pillar_gan, pillar_zhi)


def collect_pillar_shen_sha(ctx: ShenShaContext, pillar_gan: str, pillar_zhi: str) -> list[str]:
    stars: list[str] = []
    ganzhi = f"{pillar_gan}{pillar_zhi}"

    _append(stars, "\u5929\u4e59\u8d35\u4eba", pillar_zhi in TIAN_YI.get(ctx.day_gan, []))
    _append(stars, "\u6587\u660e\u8d35\u4eba", WEN_CHANG.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u592a\u6781\u8d35\u4eba", pillar_zhi in TAI_JI.get(ctx.day_gan, []))
    _append(stars, "\u56fd\u5370\u8d35\u4eba", GUO_YIN.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u91d1\u8f86", JIN_YU.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u5929\u53a8\u8d35\u4eba", TIAN_CHU.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u5b66\u5802", XUE_TANG.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u8bcd\u9986", CI_GUAN.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u7984\u795e", LU_SHEN.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u7f8a\u5203", YANG_REN.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u98de\u5203", FEI_REN.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u8840\u5203", XUE_REN.get(ctx.day_gan) == pillar_zhi)
    _append(stars, "\u7ea2\u8273", HONG_YAN.get(ctx.day_gan) == pillar_zhi)

    _append(stars, "\u5929\u5fb7\u8d35\u4eba", TIAN_DE.get(ctx.month_zhi, "") == pillar_gan)
    _append(stars, "\u6708\u5fb7\u8d35\u4eba", pillar_gan in YUE_DE.get(ctx.month_zhi, ()))
    _append(stars, "\u5929\u533b", TIAN_YI_MONTH.get(ctx.month_zhi, "") == pillar_zhi)

    _append(stars, "\u9a7e\u9a6c", _group_target(ctx.year_zhi, YI_MA_GROUPS) == pillar_zhi)
    _append(stars, "\u6843\u82b1", _group_target(ctx.year_zhi, TAO_HUA_GROUPS) == pillar_zhi)
    _append(stars, "\u534e\u76d6", _group_target(ctx.year_zhi, HUA_GAI_GROUPS) == pillar_zhi)
    _append(stars, "\u52ab\u715e", _group_target(ctx.year_zhi, JIE_SHA_GROUPS) == pillar_zhi)
    _append(stars, "\u4ea1\u795e", _group_target(ctx.year_zhi, WANG_SHEN_GROUPS) == pillar_zhi)
    _append(stars, "\u707e\u715e", _group_target(ctx.year_zhi, ZAI_SHA_GROUPS) == pillar_zhi)
    _append(stars, "\u5c06\u661f", _group_target(ctx.year_zhi, JIANG_XING_GROUPS) == pillar_zhi)
    _append(stars, "\u5c06\u661f", _group_target(ctx.day_zhi, JIANG_XING_GROUPS) == pillar_zhi)
    _append(stars, "\u5b64\u8fb0", _group_target(ctx.year_zhi, GUCHEN_GROUPS) == pillar_zhi)
    _append(stars, "\u5be1\u5bbf", _group_target(ctx.year_zhi, GUAXIU_GROUPS) == pillar_zhi)
    _append(stars, "\u7ea2\u9e1f", HONG_LUAN.get(ctx.year_zhi, "") == pillar_zhi)
    _append(stars, "\u5929\u559c", TIAN_XI.get(ctx.year_zhi, "") == pillar_zhi)

    _append(stars, "\u4e27\u95e8", _offset_zhi(ctx.year_zhi, 2) == pillar_zhi)
    _append(stars, "\u540a\u5ba2", _offset_zhi(ctx.year_zhi, -2) == pillar_zhi)
    _append(stars, "\u62ab\u9ebb", _offset_zhi(ctx.year_zhi, 3) == pillar_zhi)

    is_male = ctx.gender == 1
    if (is_male and ctx.year_gan in "\u7532\u4e19\u620a\u5e9a\u58ec") or (
        not is_male and ctx.year_gan in "\u4e59\u4e01\u5df1\u8f9b\u7678"
    ):
        _append(stars, "\u5143\u8fb0", YUAN_CHEN_FORWARD.get(ctx.year_zhi, "") == pillar_zhi)
    else:
        _append(stars, "\u5143\u8fb0", YUAN_CHEN_REVERSE.get(ctx.year_zhi, "") == pillar_zhi)

    _append(stars, "\u592d\u65fa", ganzhi in KUI_GANG)
    _append(stars, "\u65e5\u5fb7", ganzhi in RI_DE)
    _append(stars, "\u65e5\u8d35", ganzhi in RI_GUI)
    _append(stars, "\u91d1\u795e", ganzhi in JIN_SHEN)
    _append(stars, "\u5929\u8d66", ganzhi in TIAN_SHE)

    return stars
