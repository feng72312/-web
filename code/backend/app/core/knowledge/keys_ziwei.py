from __future__ import annotations

from typing import Any

ZIWEI_TOPICS = ("ziwei_palace", "ziwei_star")


def build_ziwei_lookup_keys(chart: dict[str, Any]) -> dict[str, Any]:
    palaces = chart.get("palaces") or []
    soul = palaces[0] if palaces else {}
    keys: dict[str, Any] = {
        "ziwei_palace": {"palaceName": soul.get("name", "")},
    }
    star_names: list[str] = []
    for star in soul.get("majorStars") or []:
        name = star.get("name", "")
        if name:
            star_names.append(name)
            keys.setdefault("ziwei_star", []).append({"starName": name})
    keys["star_names"] = star_names
    return keys
