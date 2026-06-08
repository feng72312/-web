from __future__ import annotations

PALACE_NAMES: tuple[str, ...] = (
    "\u547d\u5bab",
    "\u8d22\u535a",
    "\u5144\u5f1f",
    "\u7530\u5b85",
    "\u7537\u5973",
    "\u5974\u4ec6",
    "\u592b\u59bb",
    "\u75be\u5384",
    "\u8fc1\u79fb",
    "\u5b98\u7984",
    "\u798f\u5fb7",
    "\u76f8\u8c8c",
)

EARTHLY_BRANCHES: tuple[str, ...] = (
    "\u5b50",
    "\u4e11",
    "\u5bc5",
    "\u536f",
    "\u8fb0",
    "\u5df3",
    "\u5348",
    "\u672a",
    "\u7533",
    "\u9149",
    "\u620c",
    "\u4ea5",
)

_SPAN = 30.0


def palace_index_for_longitude(longitude: float, ascendant: float) -> int:
    rel = (longitude - ascendant) % 360.0
    return int(rel // _SPAN) % 12


def palace_name(index: int) -> str:
    return PALACE_NAMES[index % 12]


def palace_branch(index: int, ascendant_index: int) -> str:
    return EARTHLY_BRANCHES[(ascendant_index + index) % 12]


def build_palace_grid(ascendant: float) -> list[dict]:
    asc_index = int(ascendant // _SPAN) % 12
    palaces: list[dict] = []
    for i in range(12):
        start = (ascendant + i * _SPAN) % 360.0
        palaces.append(
            {
                "index": i,
                "name": palace_name(i),
                "branch": palace_branch(i, asc_index),
                "startLongitude": round(start, 4),
                "endLongitude": round((start + _SPAN) % 360.0, 4),
                "majorStars": [],
                "minorStars": [],
                "tags": [],
            }
        )
    return palaces


def assign_stars_to_palaces(
    palaces: list[dict],
    bodies: list[dict],
    ascendant: float,
) -> None:
    for body in bodies:
        idx = palace_index_for_longitude(body["longitude"], ascendant)
        star_entry = {"id": body["id"], "label": body["label"]}
        body["palace"] = palace_name(idx)
        if body["id"] in ("sun", "moon", "jupiter", "venus", "mars", "mercury", "saturn"):
            palaces[idx]["majorStars"].append(star_entry)
        else:
            palaces[idx]["minorStars"].append(star_entry)
