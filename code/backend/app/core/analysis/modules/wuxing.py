from __future__ import annotations

from typing import Any

from app.core.analysis.base import AnalysisModule

WUXING_KEYS = ["木", "火", "土", "金", "水"]


class WuxingAnalysisModule(AnalysisModule):
    id = "wuxing"
    name = "五行分布"
    order = 20

    def analyze(self, chart: dict[str, Any]) -> dict[str, Any]:
        counts = chart["wuxingCount"]
        total = sum(counts.values()) or 1
        items = [
            {
                "wuxing": key,
                "count": counts.get(key, 0),
                "ratio": round(counts.get(key, 0) / total, 3),
            }
            for key in WUXING_KEYS
        ]
        dominant = max(items, key=lambda x: x["count"])
        weakest = min(items, key=lambda x: x["count"])
        return {
            "items": items,
            "dominant": dominant["wuxing"],
            "weakest": weakest["wuxing"],
        }
