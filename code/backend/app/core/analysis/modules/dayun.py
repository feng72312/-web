from __future__ import annotations

from typing import Any

from app.core.analysis.base import AnalysisModule


class DayunAnalysisModule(AnalysisModule):
    id = "dayun"
    name = "大运"
    order = 40

    def analyze(self, chart: dict[str, Any]) -> dict[str, Any]:
        start = chart["dayunStart"]
        rows = chart["dayun"]
        return {
            "forward": chart["dayunForward"],
            "start": start,
            "rows": rows[:10],
        }
