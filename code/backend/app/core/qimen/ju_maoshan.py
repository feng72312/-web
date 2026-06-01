from __future__ import annotations

import datetime

from app.core.qimen.vendor import config as qcfg


def _yydun_keys() -> dict:
    return {
        tuple(qcfg.new_list(qcfg.jieqi_name, "冬至")[0:12]): "陽遁",
        tuple(qcfg.new_list(qcfg.jieqi_name, "夏至")[0:12]): "陰遁",
    }


def maoshan_yuan(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
) -> str:
    """Maoshan: first 60 hours of term = upper, next 60 = middle, rest = lower."""
    jieqi = qcfg.jq(year, month, day, hour, minute)
    dist_map, current_str = qcfg.jq_distance(year, month, day, hour, minute)
    term_start_str = dist_map.get(jieqi)
    if not term_start_str:
        return qcfg.findyuen(year, month, day, hour, minute) or "上元"
    fmt = "%Y/%m/%d %H:%M:%S"
    current_ts = datetime.datetime.strptime(current_str, fmt)
    term_start = datetime.datetime.strptime(term_start_str, fmt)
    hours = (current_ts - term_start).total_seconds() / 3600.0
    if hours < 60:
        return "上元"
    if hours < 120:
        return "中元"
    return "下元"


def qimen_ju_name_maoshan(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
) -> str:
    """Maoshan turntable ju naming (term-based yuan, same ju code table as chaibu)."""
    jieqi = qcfg.jq(year, month, day, hour, minute)
    yuan = maoshan_yuan(year, month, day, hour, minute)
    find_yingyang = qcfg.multi_key_dict_get(_yydun_keys(), jieqi) or "陽遁"
    jieqi_code = qcfg.jieqicode(year, month, day, hour, minute)
    kook = {
        "上元": jieqi_code[0],
        "中元": jieqi_code[1],
        "下元": jieqi_code[2],
    }.get(yuan, jieqi_code[0])
    return f"{find_yingyang}{kook}局{yuan}"
