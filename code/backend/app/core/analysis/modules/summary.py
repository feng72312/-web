from __future__ import annotations

from typing import Any

from app.core.analysis.base import AnalysisModule


class SummaryAnalysisModule(AnalysisModule):
    id = "summary"
    name = "命局概要"
    order = 10

    def analyze(self, chart: dict[str, Any]) -> dict[str, Any]:
        pillars = chart["pillars"]
        parts = [pillars[k]["ganzhi"] for k in ("year", "month", "day", "hour")]
        return {
            "fourPillars": " ".join(parts),
            "name": chart["input"].get("name") or "",
            "calendarType": chart["input"].get("calendarType", "solar"),
            "inputLabel": chart.get("meta", {}).get("inputLabel", ""),
            "dayMaster": chart["dayMaster"],
            "dayMasterWuxing": chart["dayMasterWuxing"],
            "lunar": chart["lunar"],
            "solar": chart["solar"],
            "dayunForward": chart["dayunForward"],
        }
