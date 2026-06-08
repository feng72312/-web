from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TianxiangInstant:
    utc_iso: str
    julian_day: float
    latitude: float
    longitude: float
    true_solar_time: str


@dataclass(frozen=True)
class MansionPlacement:
    mansion: str
    index: int
    degree_in_mansion: float


@dataclass(frozen=True)
class BodyPosition:
    id: str
    label: str
    ecliptic_longitude: float
    mansion: str
    mansion_degree: float
    retrograde: bool | None = None
