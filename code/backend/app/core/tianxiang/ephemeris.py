from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.core.tianxiang.errors import EphemerisUnavailableError, InvalidInstantError

_SWE = None
_SWE_READY = False
_SWE_ERROR = ""


def _load_swe():
    global _SWE, _SWE_READY, _SWE_ERROR
    if _SWE is not None:
        return _SWE
    try:
        import swisseph as swe

        _SWE = swe
        _SWE_READY = True
        _SWE_ERROR = ""
        return swe
    except ImportError as err:
        _SWE_READY = False
        _SWE_ERROR = str(err)
        raise EphemerisUnavailableError(
            "pyswisseph is not installed; pip install pyswisseph"
        ) from err


def configure_ephemeris(ephemeris_path: str = "") -> None:
    swe = _load_swe()
    if ephemeris_path:
        path = Path(ephemeris_path)
        if path.is_dir():
            swe.set_ephe_path(str(path))


def is_ephemeris_ready() -> bool:
    try:
        _load_swe()
        return _SWE_READY
    except EphemerisUnavailableError:
        return False


def ephemeris_error() -> str:
    return _SWE_ERROR


def datetime_to_julian(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    swe = _load_swe()
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0 + dt.microsecond / 3_600_000_000.0
    return swe.julday(dt.year, dt.month, dt.day, hour)


def sidereal_longitude(julian_day: float, body_id: int) -> tuple[float, bool | None]:
    swe = _load_swe()
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result, flag = swe.calc_ut(julian_day, body_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    if flag < 0:
        raise InvalidInstantError(f"swisseph calc failed for body {body_id}: {flag}")
    lon = float(result[0]) % 360.0
    speed = float(result[3]) if len(result) > 3 else 0.0
    retro = speed < 0 if body_id not in (swe.SUN, swe.MOON) else None
    return lon, retro


def ascendant_longitude(julian_day: float, latitude: float, longitude: float) -> float:
    swe = _load_swe()
    if not (-90.0 <= latitude <= 90.0):
        raise InvalidInstantError("latitude must be between -90 and 90")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    _cusps, ascmc = swe.houses_ex(
        julian_day,
        latitude,
        longitude,
        b"P",
        flags=swe.FLG_SIDEREAL,
    )
    return float(ascmc[0]) % 360.0


BODY_LABELS: dict[str, str] = {
    "sun": "\u65e5",
    "moon": "\u6708",
    "mercury": "\u6c34",
    "venus": "\u91d1",
    "mars": "\u706b",
    "jupiter": "\u6728",
    "saturn": "\u571f",
}
