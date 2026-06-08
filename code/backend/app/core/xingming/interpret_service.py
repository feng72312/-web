from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from app.config import settings


class XingmingInterpretService:
    RAG_CATEGORY = settings.xingming_rag_category

    def _extract_keywords(self, text: str) -> list[str]:
        tokens = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        return tokens[:12]

    def build_query(self, chart: dict[str, Any], question: str | None = None) -> str:
        inp = chart.get("input") or {}
        q = (question or inp.get("question") or "").strip()
        keywords = self._extract_keywords(q)
        kw = " ".join(keywords) if keywords else q[:40]
        ming = chart.get("mingPalace") or {}
        limits = chart.get("limits") or {}
        tai = limits.get("taiSui") or {}
        major = " ".join(s.get("label", "") for s in ming.get("majorStars") or [])
        minor = " ".join(s.get("label", "") for s in ming.get("minorStars") or [])
        parts = [
            chart.get("meta", {}).get("school", ""),
            f"\u547d\u5bab{ming.get('branch', '')}",
            major,
            minor,
            f"\u592a\u5c81{tai.get('branch', '')}",
            kw,
        ]
        return " ".join(p for p in parts if p).strip()

    def chart_key(self, chart: dict[str, Any]) -> str:
        payload = {
            "trueSolarTime": chart.get("trueSolarTime"),
            "fourPillars": chart.get("fourPillars"),
            "ascendant": (chart.get("rulesMeta") or {}).get("ascendantLongitude"),
            "school": (chart.get("meta") or {}).get("school"),
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def build_response(
        self,
        chart: dict[str, Any],
        knowledge_hits: list[dict[str, Any]],
        excerpts: list[dict[str, str]],
        cases: list[dict[str, Any]],
        summary: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "query": self.build_query(chart, chart.get("input", {}).get("question")),
            "knowledgeHits": knowledge_hits,
            "excerpts": excerpts,
            "cases": cases,
            "summary": summary,
            "agentId": agent_id,
        }
