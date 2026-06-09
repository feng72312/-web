from __future__ import annotations

from typing import Any

LIUYAO_TOPICS = ("gua", "yong_shen")


def build_liuyao_lookup_keys(chart: dict[str, Any]) -> dict[str, dict[str, str]]:
    ben = chart.get("benGua") or {}
    yong = chart.get("yongShen") or {}
    return {
        "gua": {
            "benGuaName": ben.get("name", ""),
            "lower": ben.get("lower", ""),
            "upper": ben.get("upper", ""),
        },
        "yong_shen": {
            "yongShen": yong.get("yongShen", ""),
            "relation": "general",
        },
    }
