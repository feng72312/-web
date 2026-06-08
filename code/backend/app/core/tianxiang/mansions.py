from __future__ import annotations

from app.core.tianxiang.models import MansionPlacement

MANSION_TABLE_VERSION = "guolao_v1"

# 28 mansions, equal 360/28 divisions (sidereal ecliptic).
MANSION_NAMES: tuple[str, ...] = (
    "\u89d2",
    "\u4ea2",
    "\u6c0f",
    "\u623f",
    "\u5fc3",
    "\u5c3e",
    "\u7b0b",
    "\u6597",
    "\u725b",
    "\u5973",
    "\u865a",
    "\u5371",
    "\u5ba4",
    "\u58c1",
    "\u5948",
    "\u5a41",
    "\u80c3",
    "\u6634",
    "\u6bd5",
    "\u89b4",
    "\u53c2",
    "\u4e95",
    "\u9b3c",
    "\u67f3",
    "\u661f",
    "\u5f20",
    "\u7ffc",
    "\u8f6b",
)

_SPAN = 360.0 / 28.0


def longitude_to_mansion(longitude: float, *, mansion_table: str = MANSION_TABLE_VERSION) -> MansionPlacement:
    if mansion_table != MANSION_TABLE_VERSION:
        raise ValueError(f"unsupported mansion table: {mansion_table}")
    lon = longitude % 360.0
    index = int(lon // _SPAN) % 28
    degree_in = lon - index * _SPAN
    return MansionPlacement(
        mansion=MANSION_NAMES[index],
        index=index,
        degree_in_mansion=round(degree_in, 4),
    )


def list_mansion_table(*, mansion_table: str = MANSION_TABLE_VERSION) -> list[dict[str, float | str | int]]:
    if mansion_table != MANSION_TABLE_VERSION:
        raise ValueError(f"unsupported mansion table: {mansion_table}")
    rows: list[dict[str, float | str | int]] = []
    for i, name in enumerate(MANSION_NAMES):
        rows.append(
            {
                "index": i,
                "mansion": name,
                "startLongitude": round(i * _SPAN, 4),
                "endLongitude": round((i + 1) * _SPAN, 4),
            }
        )
    return rows
