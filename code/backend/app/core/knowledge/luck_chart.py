"""Resolve dayun+liunian rows from contest/API chart payloads."""

from __future__ import annotations

from typing import Any


def get_dayun_timeline(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """Prefer luckTimeline.dayun (full liunian); fallback to top-level dayun."""
    timeline = chart.get("luckTimeline") or {}
    rows = timeline.get("dayun")
    if rows:
        return list(rows)
    return list(chart.get("dayun") or [])
