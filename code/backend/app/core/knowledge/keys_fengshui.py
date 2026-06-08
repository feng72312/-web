from __future__ import annotations

from typing import Any

FENGSHUI_TOPICS = (
    "shan",
    "ming_gua",
    "ji_xiong_fang",
    "star",
    "period",
    "scene",
)


def build_fengshui_lookup_keys(chart: dict[str, Any]) -> dict[str, Any]:
    inp = chart.get("input") or {}
    keys: dict[str, Any] = {
        "scene": {"scene": inp.get("scene", "residence")},
    }

    sitting = inp.get("sittingMountain", "")
    if sitting:
        keys["shan"] = {"mountainId": sitting.lower(), "mountain": ""}

    ming = chart.get("mingGua") or {}
    if ming.get("number") is not None:
        keys["ming_gua"] = {
            "guaNumber": str(ming.get("number", "")),
            "guaName": ming.get("name", ""),
        }

    xk = chart.get("xuankong") or {}
    period = xk.get("period") or {}
    if period.get("number") is not None:
        keys["period"] = {"period": str(period.get("number", ""))}

    stars: set[int] = set()
    for row in chart.get("directions") or []:
        label = row.get("label", "")
        if label:
            keys.setdefault("ji_xiong_labels", []).append(label)

    for pan_key in ("yunPan", "shanPan", "xiangPan", "combinedPan", "flowPan"):
        for cell in xk.get(pan_key) or []:
            for field in ("star", "yunStar", "shanStar", "xiangStar"):
                value = cell.get(field)
                if isinstance(value, int):
                    stars.add(value)
    keys["stars"] = sorted(stars)

    return keys
