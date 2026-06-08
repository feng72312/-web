from __future__ import annotations


class TianxiangError(Exception):
    """Base error for celestial ephemeris layer."""


class EphemerisUnavailableError(TianxiangError):
    """Swiss Ephemeris or star files are not available."""


class InvalidInstantError(TianxiangError):
    """Birth instant or coordinates are out of range."""
