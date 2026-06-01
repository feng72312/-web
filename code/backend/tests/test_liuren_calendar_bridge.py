from __future__ import annotations

from app.core.liuren.calendar_bridge import resolve_calendar
from app.core.liuren.models import LiurenInput


def test_resolve_calendar_four_pillars():
    inp = LiurenInput(
        question="test",
        year=2026,
        month=5,
        day=26,
        hour=12,
        minute=0,
    )
    ctx = resolve_calendar(
        year=inp.year,
        month=inp.month,
        day=inp.day,
        hour=inp.hour,
        minute=inp.minute,
        second=inp.second,
        calendar_type=inp.calendar_type,
        is_leap_month=inp.is_leap_month,
        use_true_solar_time=inp.use_true_solar_time,
        longitude=inp.longitude,
    )
    assert ctx.day_ganzhi
    assert ctx.hour_ganzhi
    assert ctx.jieqi
    assert ctx.four_pillars["day"]
