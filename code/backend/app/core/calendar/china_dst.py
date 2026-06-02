from __future__ import annotations

from datetime import datetime, timedelta

# China daylight saving time (approximate civil midnight boundaries, local time).
_DST_RANGES: tuple[tuple[datetime, datetime], ...] = (
    (datetime(1986, 5, 4, 2, 0, 0), datetime(1986, 9, 14, 2, 0, 0)),
    (datetime(1987, 4, 12, 2, 0, 0), datetime(1987, 9, 13, 2, 0, 0)),
    (datetime(1988, 4, 10, 2, 0, 0), datetime(1988, 9, 11, 2, 0, 0)),
    (datetime(1989, 4, 16, 2, 0, 0), datetime(1989, 9, 17, 2, 0, 0)),
    (datetime(1990, 4, 15, 2, 0, 0), datetime(1990, 9, 16, 2, 0, 0)),
    (datetime(1991, 4, 14, 2, 0, 0), datetime(1991, 9, 15, 2, 0, 0)),
)


def apply_china_dst(dt: datetime) -> datetime:
    """Convert clock time during DST periods to standard China time."""
    for start, end in _DST_RANGES:
        if start <= dt < end:
            return dt - timedelta(hours=1)
    return dt
