from __future__ import annotations

from typing import Any

from app.core.liuren.calendar_bridge import LiurenCalendarContext, resolve_calendar
from app.core.liuren.models import (
    JinkouChart,
    LiurenChart,
    LiurenInput,
    LiurenResult,
)
from app.core.liuren.shensha import YUE_JIANG_NAMES, collect_shen_sha
from app.core.liuren.vendor.kinliuren_core import Liuren

GENERAL_S2T = {
    "貴": "贵人",
    "蛇": "螣蛇",
    "雀": "朱雀",
    "合": "六合",
    "勾": "勾陈",
    "龍": "青龙",
    "空": "天空",
    "虎": "白虎",
    "常": "太常",
    "玄": "玄武",
    "陰": "太阴",
    "后": "天后",
}


def _norm_general(name: str) -> str:
    if not name:
        return name
    return GENERAL_S2T.get(name, name)


def _norm_ke_entry(entry: list) -> dict[str, Any]:
    if not entry or len(entry) < 2:
        return {"pair": "", "general": ""}
    pair = entry[0] if isinstance(entry[0], str) else str(entry[0])
    gen = _norm_general(entry[1] if len(entry) > 1 else "")
    return {"pair": pair, "general": gen}


def _norm_chuan(block: dict) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, label in (("初傳", "chu"), ("中傳", "zhong"), ("末傳", "mo")):
        row = block.get(key) or []
        if len(row) >= 4:
            out[label] = {
                "zhi": row[0],
                "general": _norm_general(row[1]),
                "liuQin": row[2],
                "xunKong": row[3],
            }
    return out


def _build_liuren_chart(
    data: LiurenInput, ctx: LiurenCalendarContext
) -> LiurenChart:
    lr = Liuren(ctx.jieqi, ctx.lunar_month, ctx.day_ganzhi, ctx.hour_ganzhi)
    raw = lr.result(data.gui_ren_mode)

    mg_zhi = lr.moongeneral()
    yue_jiang = YUE_JIANG_NAMES.get(mg_zhi, mg_zhi)

    sike_raw = raw.get("四課") or {}
    si_ke = {
        "yi": _norm_ke_entry(sike_raw.get("一課")),
        "er": _norm_ke_entry(sike_raw.get("二課")),
        "san": _norm_ke_entry(sike_raw.get("三課")),
        "si": _norm_ke_entry(sike_raw.get("四課")),
    }

    san_chuan = _norm_chuan(raw.get("三傳") or {})
    tdp = raw.get("天地盤") or {}
    earth = tdp.get("地盤") or []
    sky = tdp.get("天盤") or []
    gens = [_norm_general(g) for g in (tdp.get("天將") or [])]
    di_zhuan = raw.get("地轉天盤") or {}
    jiang_zhuan = raw.get("地轉天將") or {}

    palaces = []
    zhi_order = list(di_zhuan.keys()) if di_zhuan else earth
    for zhi in zhi_order:
        palaces.append(
            {
                "earth": zhi,
                "sky": di_zhuan.get(zhi, ""),
                "general": _norm_general(jiang_zhuan.get(zhi, "")),
            }
        )

    ge = raw.get("格局") or []
    ge_ju = {
        "name": ge[0] if len(ge) > 0 else "",
        "sub": ge[1] if len(ge) > 1 else "",
    }

    shen_sha = collect_shen_sha(lr, raw)

    return LiurenChart(
        input=data,
        four_pillars=ctx.four_pillars,
        jieqi=ctx.jieqi,
        lunar_month=ctx.lunar_month,
        yue_jiang=yue_jiang,
        si_ke=si_ke,
        san_chuan=san_chuan,
        tian_di_pan={
            "earth": earth,
            "sky": sky,
            "generals": gens,
            "palaces": palaces,
        },
        ge_ju=ge_ju,
        shen_sha=shen_sha,
        true_solar_time=ctx.true_solar_time,
        meta={
            "rules": "月将加时九宗门",
            "guiRenMode": data.gui_ren_mode,
            "category": data.category,
        },
    )


def _build_jinkou_chart(
    data: LiurenInput, ctx: LiurenCalendarContext
) -> JinkouChart:
    difen = data.jinkou_difen.strip() or ctx.hour_zhi
    if difen not in "子丑寅卯辰巳午未申酉戌亥":
        difen = ctx.hour_zhi
    lr = Liuren(ctx.jieqi, ctx.lunar_month, ctx.day_ganzhi, ctx.hour_ganzhi)
    raw = lr.jinkou(difen)
    gui = raw.get("貴神") or ["", ""]
    jiang = raw.get("將神") or ["", ""]
    return JinkouChart(
        ren_yuan=str(raw.get("人元", "")),
        gui_shen=[str(gui[0]), _norm_general(str(gui[1]))],
        jiang_shen=[str(jiang[0]), str(jiang[1])],
        difen=str(raw.get("地分", difen)),
        four_pillars=ctx.four_pillars,
    )


def build_chart(data: LiurenInput) -> LiurenResult:
    ctx = resolve_calendar(
        year=data.year,
        month=data.month,
        day=data.day,
        hour=data.hour,
        minute=data.minute,
        second=data.second,
        calendar_type=data.calendar_type,
        is_leap_month=data.is_leap_month,
        use_true_solar_time=data.use_true_solar_time,
        longitude=data.longitude,
    )

    liuren_part = None
    jinkou_part = None
    if data.cast_method in ("liuren", "both"):
        liuren_part = _build_liuren_chart(data, ctx)
    if data.cast_method in ("jinkou", "both"):
        jinkou_part = _build_jinkou_chart(data, ctx)

    return LiurenResult(
        input=data,
        liuren=liuren_part,
        jinkou=jinkou_part,
        true_solar_time=ctx.true_solar_time,
        meta={"civilTime": ctx.civil_time},
    )
