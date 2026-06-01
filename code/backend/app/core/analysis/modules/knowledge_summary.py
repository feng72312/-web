from __future__ import annotations

from typing import Any

from app.core.analysis.base import AnalysisModule
from app.core.knowledge.factory import get_knowledge_service


class KnowledgeSummaryModule(AnalysisModule):
    id = "knowledge_summary"
    name = "典籍结构化"
    order = 25

    def analyze(self, chart: dict[str, Any]) -> dict[str, Any]:
        service = get_knowledge_service()
        if not service.enabled:
            return {
                "enabled": False,
                "hit": None,
                "agreementLevel": None,
                "safeAutoAnswer": False,
                "displaySummary": "",
                "missingTopics": ["tiaohou", "shishen", "ganzhi"],
            }

        result = service.lookup_chart(chart)
        tiaohou_hits = [hit for hit in result.hits if hit.topic == "tiaohou"]
        primary = tiaohou_hits[0] if tiaohou_hits else None
        return {
            "enabled": True,
            "hit": primary.model_dump() if primary else None,
            "hitsCount": len(result.hits),
            "agreementLevel": primary.agreementLevel if primary else None,
            "safeAutoAnswer": primary.safeAutoAnswer if primary else False,
            "displaySummary": primary.summary if primary else "",
            "autoAnswerSummary": result.autoAnswerSummary,
            "missingTopics": result.missingTopics,
        }
