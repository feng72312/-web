from __future__ import annotations

"""Guolao-style four remainders (si yu) on sidereal ecliptic."""

from datetime import datetime, timezone

SI_YU_MODEL = "guolao_v1"

# Reference: J2000 purple qi at 0 deg; 28-year cycle (~10227.179 days).
_ZIQI_BASE = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
_ZIQI_BASE_DEG = 0.0
_ZIQI_PERIOD_DAYS = 10227.179

# Mean lunar apogee (yue bei) mean motion ~40.69 deg/year from J2000 anchor.
_YUEBEI_BASE = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
_YUEBEI_BASE_DEG = 90.0
_YUEBEI_DEG_PER_DAY = 40.6905 / 365.25


def _days_since(base: datetime, target: datetime) -> float:
    return (target - base).total_seconds() / 86400.0


def purple_qi_longitude(dt: datetime, *, model: str = SI_YU_MODEL) -> float:
    if model != SI_YU_MODEL:
        raise ValueError(f"unsupported si yu model: {model}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    days = _days_since(_ZIQI_BASE, dt.astimezone(timezone.utc))
    movement = (days / _ZIQI_PERIOD_DAYS) * 360.0
    return (_ZIQI_BASE_DEG - movement) % 360.0


def yue_bei_longitude(dt: datetime, *, model: str = SI_YU_MODEL) -> float:
    if model != SI_YU_MODEL:
        raise ValueError(f"unsupported si yu model: {model}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    days = _days_since(_YUEBEI_BASE, dt.astimezone(timezone.utc))
    return (_YUEBEI_BASE_DEG + days * _YUEBEI_DEG_PER_DAY) % 360.0


def rahu_from_ketu(ketu_longitude: float) -> float:
    """Luo hou opposite ji du (apogee) in guolao_v1."""
    return (ketu_longitude + 180.0) % 360.0
