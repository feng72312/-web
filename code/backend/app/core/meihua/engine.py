from __future__ import annotations

from app.core.liuyao.calendar_ctx import calendar_for_chart
from app.core.liuyao.models import LiuyaoInput
from app.core.meihua.casting import cast_meihua_lines
from app.core.meihua.models import MeihuaChart, MeihuaInput
from app.core.meihua.ti_yong import build_chart_parts


class MeihuaEngine:
    """Meihua Yixue chart builder (Shao Yong style number/time cast)."""

    def divine(self, data: MeihuaInput) -> MeihuaChart:
        line_values, cast_note = cast_meihua_lines(data)
        parts = build_chart_parts(
            line_values,
            moving_override=data.moving_position_override,
        )
        calendar = calendar_for_chart(
            LiuyaoInput(
                question=data.question,
                method=data.method,
                numbers=data.numbers,
                year=data.year,
                month=data.month,
                day=data.day,
                hour=data.hour,
                minute=data.minute,
                second=data.second,
                calendar_type=data.calendar_type,
                is_leap_month=data.is_leap_month,
            )
        )
        meta = {
            "rules": "梅花易数体用",
            "castNote": cast_note,
            "lineValues": line_values,
            "tiYongMeta": parts["ti_meta"],
            "monthJian": calendar.get("monthJian", ""),
            "dayChen": calendar.get("dayChen", ""),
        }
        return MeihuaChart(
            input=data,
            ben_gua=parts["ben"],
            bian_gua=parts["bian"],
            lines=parts["lines"],
            moving_lines=parts["moving"],
            ti_gua=parts["ti"],
            yong_gua=parts["yong"],
            ti_yong_relation=parts["relation"],
            hu_gua=parts["hu"],
            is_static=parts["is_static"],
            meta=meta,
        )
