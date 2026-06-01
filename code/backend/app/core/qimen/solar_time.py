from __future__ import annotations

from datetime import datetime, timedelta


def apply_true_solar_time(
    dt: datetime,
    longitude: float,
    standard_longitude: float = 120.0,
) -> datetime:
    """Longitude correction (minutes): 4 min per degree east/west of standard meridian."""
    offset_minutes = (longitude - standard_longitude) * 4.0
    return dt + timedelta(minutes=offset_minutes)


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")
