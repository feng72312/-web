from __future__ import annotations

from typing import Any

from app.core.ziwei.calendar_bridge import ZiweiCalendarContext
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.mutagen_tables import apply_mutagen_table_to_chart
from app.core.ziwei.rules import ZiweiRules


def build_chart(
    ctx: ZiweiCalendarContext,
    data: ZiweiInput,
    rules: ZiweiRules,
) -> Any:
    try:
        from iztro_py import astro
        from iztro_py.i18n import set_language
    except ImportError as err:
        raise RuntimeError("iztro-py is not installed") from err

    set_language("zh-CN")
    fix_leap = rules.iztro_fix_leap()
    chart = astro.by_solar(
        ctx.solar_date_str,
        ctx.time_index,
        ctx.gender_label,
        fix_leap=fix_leap,
        language="zh-CN",
    )
    apply_mutagen_table_to_chart(chart, rules.mutagen_table)
    return chart


def build_horoscope(chart: Any, target_date: str) -> Any:
    return chart.horoscope(target_date)
