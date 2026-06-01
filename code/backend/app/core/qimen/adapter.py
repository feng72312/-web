from __future__ import annotations

import re
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from lunar_python import Lunar, Solar

from app.core.qimen.models import (
    JuInfo,
    PalaceCell,
    QimenChart,
    QimenInput,
    ZhiFuZhiShi,
)
from app.core.qimen.ju_maoshan import maoshan_yuan, qimen_ju_name_maoshan
from app.core.qimen.solar_time import apply_true_solar_time, format_datetime
from app.core.qimen.vendor import config as qcfg
from app.core.qimen.vendor.kinqimen_core import Qimen

PALACE_INDEX = {
    "坎": 1,
    "坤": 2,
    "震": 3,
    "巽": 4,
    "中": 5,
    "乾": 6,
    "兑": 7,
    "艮": 8,
    "离": 9,
}

STAR_LABEL = {
    "蓬": "天蓬",
    "芮": "天芮",
    "冲": "天冲",
    "辅": "天辅",
    "禽": "天禽",
    "心": "天心",
    "柱": "天柱",
    "任": "天任",
    "英": "天英",
}

DOOR_LABEL = {
    "休": "休门",
    "生": "生门",
    "伤": "伤门",
    "杜": "杜门",
    "景": "景门",
    "死": "死门",
    "惊": "惊门",
    "开": "开门",
}

GOD_LABEL = {
    "符": "值符",
    "蛇": "螣蛇",
    "阴": "太阴",
    "合": "六合",
    "勾": "勾陈",
    "雀": "朱雀",
    "地": "九地",
    "天": "九天",
    "虎": "白虎",
    "玄": "玄武",
}


def resolve_solar_datetime(data: QimenInput) -> tuple[datetime, str]:
    if data.calendar_type == "lunar":
        lunar = Lunar.fromYmdHms(
            data.year,
            data.month,
            data.day,
            data.hour,
            data.minute,
            data.second,
        )
        solar = lunar.getSolar()
        dt = datetime(
            solar.getYear(),
            solar.getMonth(),
            solar.getDay(),
            solar.getHour(),
            solar.getMinute(),
            solar.getSecond(),
        )
    else:
        dt = datetime(
            data.year,
            data.month,
            data.day,
            data.hour,
            data.minute,
            data.second,
        )
    civil = format_datetime(dt)
    if data.use_true_solar_time:
        dt = apply_true_solar_time(dt, data.longitude)
    return dt, civil


def _method_option(method: str) -> int:
    return {"chaibu": 1, "zhirun": 2}.get(method, 1)


def _normalize_sky(raw: Any) -> dict[str, str]:
    if isinstance(raw, tuple):
        raw = raw[0]
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def _build_human_plate(
    earth: dict[str, str],
    heaven: dict[str, str],
    hour_gan: str,
) -> dict[str, str]:
    """Human plate: hour stem palace on earth, then align with heaven rotation."""
    if not earth or not heaven:
        return {}
    start_gong = None
    for gong, stem in earth.items():
        if stem == hour_gan:
            start_gong = gong
            break
    if start_gong is None:
        return dict(heaven)
    stems = list(earth.values())
    gongs = list(earth.keys())
    if start_gong not in gongs:
        return dict(heaven)
    idx = gongs.index(start_gong)
    rotated_stems = gongs[idx:] + gongs[:idx]
    stem_order = [earth[g] for g in rotated_stems]
    rotate = qcfg.clockwise_eightgua
    if start_gong in rotate:
        gong_order = qcfg.new_list(rotate, start_gong)
        mapping = dict(zip(gong_order, stem_order[: len(gong_order)]))
        if "中" in earth:
            mapping["中"] = earth.get("中", "")
        return mapping
    return dict(heaven)


def _parse_ju_name(ju_name: str) -> JuInfo:
    m = re.match(r"(阳遁|阴遁|陽遁|陰遁)([一二三四五六七八九])局(上元|中元|下元)", ju_name)
    cn_num = {
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
    }
    if not m:
        return JuInfo("陽遁", 1, "上元", "", ju_name)
    dun = m.group(1).replace("阳", "陽").replace("阴", "陰")
    num = cn_num.get(m.group(2), 1)
    yuan = m.group(3)
    return JuInfo(dun, num, yuan, "", ju_name)


@contextmanager
def _pan_ju_patch(data: QimenInput, dt: datetime):
    orig_chaibu = qcfg.qimen_ju_name_chaibu
    orig_zhirun = qcfg.qimen_ju_name_zhirun

    def _resolve_ju_name(
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
    ) -> str:
        if data.method == "maoshan":
            return qimen_ju_name_maoshan(year, month, day, hour, minute)
        if data.method == "zhirun":
            return orig_zhirun(year, month, day, hour, minute)
        return orig_chaibu(year, month, day, hour, minute)
    forced: str | None = None
    if data.ju_override is not None and 1 <= data.ju_override <= 9:
        cn = "一二三四五六七八九"[data.ju_override - 1]
        jieqi = qcfg.jq(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        yydun = {
            tuple(qcfg.new_list(qcfg.jieqi_name, "冬至")[0:12]): "陽遁",
            tuple(qcfg.new_list(qcfg.jieqi_name, "夏至")[0:12]): "陰遁",
        }
        dun_raw = qcfg.multi_key_dict_get(yydun, jieqi) or "陽遁"
        dun = dun_raw.replace("阳", "陽").replace("阴", "陰")
        if data.method == "maoshan":
            yuan = maoshan_yuan(
                dt.year, dt.month, dt.day, dt.hour, dt.minute
            )
        else:
            yuan = qcfg.findyuen(
                dt.year, dt.month, dt.day, dt.hour, dt.minute
            )
        forced = f"{dun}{cn}局{yuan}"

    def _patched(year, month, day, hour, minute):
        if forced:
            return forced
        return _resolve_ju_name(year, month, day, hour, minute)

    qcfg.qimen_ju_name_chaibu = _patched
    qcfg.qimen_ju_name_zhirun = _patched
    try:
        yield
    finally:
        qcfg.qimen_ju_name_chaibu = orig_chaibu
        qcfg.qimen_ju_name_zhirun = orig_zhirun


def build_chart(data: QimenInput) -> QimenChart:
    dt, civil_time = resolve_solar_datetime(data)
    option = _method_option(data.method)

    with _pan_ju_patch(data, dt):
        qm = Qimen(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        raw = qm.pan(option)

    gz = qcfg.gangzhi(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    ju_name = str(raw.get("排局", ""))
    ju = _parse_ju_name(ju_name)
    ju.jieqi = str(raw.get("节气", ""))
    ju.fu_tou = gz[2]
    ju.xun_shou = str(raw.get("旬首", ""))

    zfzs = raw.get("值符值使") or {}
    star_gong = zfzs.get("值符星宮") or ["", ""]
    door_gong = zfzs.get("值使門宮") or ["", ""]
    zhi_fu_gan_pair = zfzs.get("值符天干") or ["", ""]
    zhi_fu_zhi_shi = ZhiFuZhiShi(
        zhi_fu_star=STAR_LABEL.get(str(star_gong[0]), str(star_gong[0])),
        zhi_fu_gong=str(star_gong[1]),
        zhi_fu_gan=str(zhi_fu_gan_pair[1] if len(zhi_fu_gan_pair) > 1 else ""),
        zhi_shi_door=DOOR_LABEL.get(str(door_gong[0]), str(door_gong[0])),
        zhi_shi_gong=str(door_gong[1]),
    )

    earth = {str(k): str(v) for k, v in (raw.get("地盤") or {}).items()}
    heaven = _normalize_sky(raw.get("天盤"))
    human = _build_human_plate(earth, heaven, gz[3][0])
    stars = {str(k): str(v) for k, v in (raw.get("星") or {}).items()}
    doors = {str(k): str(v) for k, v in (raw.get("門") or {}).items()}
    gods = {str(k): str(v) for k, v in (raw.get("神") or {}).items()}

    palace_names = ["巽", "离", "坤", "震", "中", "兑", "艮", "坎", "乾"]
    palaces: list[PalaceCell] = []
    for name in palace_names:
        idx = PALACE_INDEX.get(name, 5)
        star_raw = stars.get(name, "")
        palaces.append(
            PalaceCell(
                index=idx,
                name=name,
                earth=earth.get(name, ""),
                heaven=heaven.get(name, ""),
                human=human.get(name, heaven.get(name, "")),
                star=STAR_LABEL.get(star_raw, star_raw),
                door=DOOR_LABEL.get(doors.get(name, ""), doors.get(name, "")),
                god=GOD_LABEL.get(gods.get(name, ""), gods.get(name, "")),
            )
        )

    four_pillars = {
        "year": gz[0],
        "month": gz[1],
        "day": gz[2],
        "hour": gz[3],
    }
    method_labels = {
        "chaibu": "拆补",
        "zhirun": "置闰",
        "maoshan": "茅山转盘",
    }
    meta = {
        "rules": "时家奇门拆补置闰茅山",
        "method": data.method,
        "methodLabel": method_labels.get(data.method)
        or raw.get("排盤方式", ""),
        "category": data.category,
        "direction": data.direction,
        "civilTime": civil_time,
        "juDay": raw.get("局日", ""),
        "xunKong": raw.get("旬空", {}),
        "maXing": raw.get("馬星", {}),
        "debugJuOverride": data.ju_override is not None,
        "humanPlateNote": "人盘按时干落宫与地盘旋布",
    }
    if data.ju_override is not None:
        meta["juOverrideApplied"] = True

    return QimenChart(
        input=data,
        ju=ju,
        zhi_fu_zhi_shi=zhi_fu_zhi_shi,
        palaces=palaces,
        four_pillars=four_pillars,
        true_solar_time=format_datetime(dt),
        meta=meta,
    )
