from __future__ import annotations

from datetime import datetime

from app.core.tianxiang.errors import EphemerisUnavailableError
from app.core.tianxiang.models import TianxiangInstant
from app.core.tianxiang.service import TianxiangService
from app.core.xingming.calendar_bridge import resolve_calendar
from app.core.xingming.models import XingmingChartResult, XingmingInput
from app.core.xingming.normalize import normalize_chart


class XingmingEngine:
    def __init__(self, tianxiang: TianxiangService | None = None) -> None:
        self._tianxiang = tianxiang
        self._tianxiang_error: str | None = None
        if self._tianxiang is None:
            try:
                self._tianxiang = TianxiangService()
            except EphemerisUnavailableError as err:
                self._tianxiang_error = str(err)

    def chart(self, data: XingmingInput) -> XingmingChartResult:
        if self._tianxiang is None:
            raise RuntimeError(self._tianxiang_error or "tianxiang service unavailable")
        ctx = resolve_calendar(data, data.rules)
        instant = TianxiangInstant(
            utc_iso=ctx.utc_iso,
            julian_day=ctx.julian_day,
            latitude=ctx.latitude,
            longitude=ctx.longitude,
            true_solar_time=ctx.true_solar_time,
        )
        positions = self._tianxiang.compute_positions(instant)
        asc = self._tianxiang.ascendant(instant)
        bodies = [
            {
                "id": p.id,
                "label": p.label,
                "longitude": p.ecliptic_longitude,
                "mansion": p.mansion,
                "mansionDegree": p.mansion_degree,
                "retrograde": p.retrograde,
            }
            for p in positions
        ]
        target_year = data.target_year
        if target_year is None:
            target_year = datetime.strptime(ctx.true_solar_time, "%Y-%m-%d %H:%M:%S").year
        payload = normalize_chart(ctx, data, data.rules, bodies, asc, target_year)
        return XingmingChartResult(chart=payload)
