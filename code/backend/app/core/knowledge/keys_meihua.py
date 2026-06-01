from __future__ import annotations

from typing import Any

MEIHUA_TOPICS = ("gua", "ti_yong", "leixiang")


def build_meihua_lookup_keys(chart: dict[str, Any]) -> dict[str, dict[str, str]]:
    ben = chart.get("benGua") or {}
    ti = chart.get("tiGua") or {}
    yong = chart.get("yongGua") or {}
    keys: dict[str, dict[str, str]] = {
        "gua": {
            "benGuaName": ben.get("name", ""),
            "lower": ben.get("lower", ""),
            "upper": ben.get("upper", ""),
        },
        "ti_yong": {
            "tiGua": ti.get("name", ""),
            "yongGua": yong.get("name", ""),
            "relation": chart.get("tiYongRelation", ""),
        },
    }
    if ti.get("name") and yong.get("name"):
        keys["leixiang"] = {
            "tiElement": ti.get("element", ""),
            "yongElement": yong.get("element", ""),
        }
    return keys
