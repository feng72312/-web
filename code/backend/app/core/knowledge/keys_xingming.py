from __future__ import annotations

from typing import Any

XINGMING_TOPICS = (
    "shou_ming",
    "palace",
    "si_yu",
    "tai_sui",
    "mansion",
)


def build_xingming_lookup_keys(chart: dict[str, Any]) -> dict[str, Any]:
    ming = chart.get("mingPalace") or {}
    limits = chart.get("limits") or {}
    tai = limits.get("taiSui") or {}
    keys: dict[str, Any] = {
        "palace": {
            "palaceName": ming.get("name", ""),
            "branch": ming.get("branch", ""),
        },
        "tai_sui": {"branch": tai.get("branch", "")},
    }
    star_ids: list[str] = []
    for star in (ming.get("majorStars") or []) + (ming.get("minorStars") or []):
        sid = star.get("id")
        if sid:
            star_ids.append(sid)
            keys.setdefault("shou_ming", []).append({"starId": sid})
    keys["star_ids"] = star_ids

    sun = next((b for b in chart.get("bodies") or [] if b.get("id") == "sun"), None)
    if sun and sun.get("mansion"):
        keys["mansion"] = {"mansion": sun["mansion"]}

    for body in chart.get("bodies") or []:
        if body.get("id") in ("rahu", "ketu", "yuebei", "ziqi"):
            keys.setdefault("si_yu", []).append({"starId": body["id"]})

    return keys
