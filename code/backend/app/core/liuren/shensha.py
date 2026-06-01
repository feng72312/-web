from __future__ import annotations

from typing import Any

from app.core.liuren.vendor.kinliuren_core import Liuren

YUE_JIANG_NAMES = {
    "子": "神后",
    "丑": "大吉",
    "寅": "功曹",
    "卯": "太冲",
    "辰": "天罡",
    "巳": "太乙",
    "午": "胜光",
    "未": "小吉",
    "申": "传送",
    "酉": "从魁",
    "戌": "河魁",
    "亥": "登明",
}


def _safe_call(fn, default: str = "") -> str:
    try:
        val = fn()
        return str(val) if val is not None else default
    except Exception:
        return default


def collect_shen_sha(lr: Liuren, raw: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}

    if raw.get("日馬"):
        out["日马"] = str(raw["日馬"])
    out["月马"] = _safe_call(lr.moonhorse)
    out["丁马"] = _safe_call(lr.dinhorse)
    out["天马"] = _safe_call(lr.dayhorse)
    out["华盖"] = _safe_call(lr.wahgai)
    out["闪电"] = _safe_call(lr.lightning)

    day = lr.daygangzhi
    hour = lr.hourgangzhi
    out["日干支"] = day
    out["时干支"] = hour

    try:
        out["季"] = _safe_call(lambda: lr.find_season(day[1]))
    except Exception:
        pass

    try:
        hs = lr.hoursu
        day_gan = day[0]
        hour_zhi = hour[1]
        for key_tuple, mapping in hs.items():
            if day_gan in key_tuple:
                out["宿"] = mapping.get(hour_zhi, "")
                break
    except Exception:
        pass

    try:
        gui_start = lr.guiren_starting_gangzhi(0)
        out["贵人"] = gui_start or ""
        out["贵人宫"] = _safe_call(lambda: lr.guiren_start_earth(0))
    except Exception:
        pass

    chong_map = {
        "子午": "午",
        "丑未": "未",
        "寅申": "申",
        "卯酉": "酉",
        "辰戌": "戌",
        "巳亥": "亥",
    }
    for pair, target in chong_map.items():
        if day[1] in pair and hour[1] in pair:
            out["冲"] = target
            break

    he_map = dict(zip("子丑午未巳申寅亥卯戌辰酉", "丑子未午申巳亥寅戌卯酉辰"))
    if he_map.get(day[1]) == hour[1]:
        out["合"] = hour[1]

    try:
        pair = (day[1], hour[1])
        rev = (hour[1], day[1])
        if pair in lr.ying_chong:
            out["刑"] = lr.ying_chong[pair]
        elif rev in lr.ying_chong:
            out["刑"] = lr.ying_chong[rev]
    except Exception:
        pass

    try:
        if lr.hai.get(day[1]) == hour[1]:
            out["害"] = hour[1]
    except Exception:
        pass

    try:
        if lr.po.get(day[1]) == hour[1]:
            out["破"] = day[1]
    except Exception:
        pass

    try:
        ym = lr.yima_dict.get(day[1], "")
        if ym:
            out["驿马"] = ym
    except Exception:
        pass

    sc = raw.get("三傳") or {}
    for label, key in (("初传", "初傳"), ("中传", "中傳"), ("末传", "末傳")):
        row = sc.get(key) or []
        if len(row) >= 4:
            xk = row[3]
            if xk:
                out[f"{label}旬空"] = str(xk)

    mg = lr.moongeneral()
    out["月将"] = YUE_JIANG_NAMES.get(mg, mg)
    out["月将宫"] = mg

    try:
        mu = lr.shigangjigong.get(day[1], "")
        if mu:
            out["日墓"] = mu
    except Exception:
        pass

    return {k: v for k, v in out.items() if v}
