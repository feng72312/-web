from __future__ import annotations

from datetime import datetime

from app.core.ziwei.calendar_bridge import resolve_calendar
from app.core.ziwei.models import ZiweiChartResult, ZiweiInput
from app.core.ziwei.normalize import normalize_chart
from app.core.ziwei.vendor.iztro_adapter import build_chart, build_horoscope


class ZiweiEngine:
    def chart(self, data: ZiweiInput) -> ZiweiChartResult:
        ctx = resolve_calendar(data, data.rules)
        raw = build_chart(ctx, data, data.rules)
        target_year = data.target_year
        if target_year is None:
            target_year = datetime.strptime(ctx.true_solar_time, "%Y-%m-%d %H:%M:%S").year
        parts = ctx.true_solar_time.split(" ")[0].split("-")
        month = int(parts[1]) if len(parts) > 1 else 6
        day = int(parts[2]) if len(parts) > 2 else 1
        horoscope_date = f"{target_year}-{month}-{day}"
        horoscope = build_horoscope(raw, horoscope_date)
        payload = normalize_chart(
            raw,
            horoscope,
            ctx,
            data.to_dict(),
            data.rules,
            target_year,
        )
        return ZiweiChartResult(chart=payload)
