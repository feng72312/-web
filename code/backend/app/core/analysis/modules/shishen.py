from __future__ import annotations

from typing import Any

from app.core.analysis.base import AnalysisModule

PILLAR_LABELS = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "hour": "时柱",
}


class ShishenAnalysisModule(AnalysisModule):
    id = "shishen"
    name = "十神"
    order = 30

    def analyze(self, chart: dict[str, Any]) -> dict[str, Any]:
        pillars = chart["pillars"]
        rows = []
        for key in ("year", "month", "day", "hour"):
            pillar = pillars[key]
            rows.append(
                {
                    "pillar": PILLAR_LABELS[key],
                    "ganzhi": pillar["ganzhi"],
                    "shishenGan": pillar["shishenGan"] or "日主",
                    "shishenZhi": pillar["shishenZhi"],
                }
            )
        return {"rows": rows}
