from __future__ import annotations

from typing import Any

QIMEN_TOPICS = ("ju", "men", "xing", "shen", "yong")


def build_qimen_lookup_keys(chart: dict[str, Any]) -> dict[str, Any]:
    ju = chart.get("ju") or {}
    inp = chart.get("input") or {}
    keys: dict[str, Any] = {
        "ju": {
            "dunType": ju.get("dunType", ""),
            "juNumber": str(ju.get("juNumber", "")),
            "yuan": ju.get("yuan", ""),
            "jieqi": ju.get("jieqi", ""),
        },
        "yong": {
            "category": inp.get("category", "shizhan"),
        },
    }
    doors: list[str] = []
    stars: list[str] = []
    gods: list[str] = []
    for p in chart.get("palaces", []):
        door = p.get("door", "")
        star = p.get("star", "")
        god = p.get("god", "")
        if door and door not in doors:
            doors.append(door)
        if star and star not in stars:
            stars.append(star)
        if god and god not in gods:
            gods.append(god)
    keys["doors"] = doors
    keys["stars"] = stars
    keys["gods"] = gods
    return keys
