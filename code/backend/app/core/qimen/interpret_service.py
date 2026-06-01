from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class QimenInterpretService:
    RAG_CATEGORY = "04奇门遁甲"

    def build_query(self, chart: dict[str, Any], question: str | None = None) -> str:
        ju = chart.get("ju", {})
        zf = chart.get("zhiFuZhiShi", {})
        inp = chart.get("input", {})
        q = question or inp.get("question", "")
        keywords = self._extract_keywords(q)
        keyword_text = " ".join(keywords) if keywords else q[:40]
        category = inp.get("category", "shizhan")
        cat_label = "事占" if category == "shizhan" else "行占"
        doors = " ".join(
            f"{p.get('name', '')}{p.get('door', '')}"
            for p in chart.get("palaces", [])
            if p.get("door")
        )
        return (
            f"{ju.get('juName', '')} {ju.get('jieqi', '')} "
            f"值符{zf.get('zhiFuStar', '')}落{zf.get('zhiFuGong', '')} "
            f"值使{zf.get('zhiShiDoor', '')}落{zf.get('zhiShiGong', '')} "
            f"{cat_label} {inp.get('direction', '')} {doors} {keyword_text}"
        )

    def chart_key(self, chart: dict[str, Any]) -> str:
        payload = {
            "juName": chart.get("ju", {}).get("juName"),
            "trueSolarTime": chart.get("trueSolarTime"),
            "fourPillars": chart.get("fourPillars"),
            "question": chart.get("input", {}).get("question"),
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def build_response(
        self,
        chart: dict[str, Any],
        knowledge_hits: list[dict[str, Any]],
        excerpts: list[dict[str, str]],
        summary: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        ju = chart.get("ju", {})
        zf = chart.get("zhiFuZhiShi", {})
        payload: dict[str, Any] = {
            "query": self.build_query(chart),
            "ju": ju,
            "zhiFuZhiShi": zf,
            "knowledgeHits": knowledge_hits,
            "excerpts": excerpts,
            "summary": summary or self._fallback_summary(chart, excerpts),
        }
        if agent_id:
            payload["agentId"] = agent_id
        return payload

    def _extract_keywords(self, question: str) -> list[str]:
        tokens = re.findall(r"[\u4e00-\u9fff]{2,}", question)
        stop = {"什么", "怎么", "是否", "能不能", "可以", "这次", "请问"}
        return [token for token in tokens if token not in stop][:5]

    def _fallback_summary(
        self, chart: dict[str, Any], excerpts: list[dict[str, str]]
    ) -> str:
        ju = chart.get("ju", {})
        zf = chart.get("zhiFuZhiShi", {})
        excerpt_hint = excerpts[0].get("excerpt", "")[:80] if excerpts else ""
        return (
            f"{ju.get('juName', '')}, 节气{ju.get('jieqi', '')}, "
            f"值符{zf.get('zhiFuStar', '')}在{zf.get('zhiFuGong', '')}, "
            f"值使{zf.get('zhiShiDoor', '')}在{zf.get('zhiShiGong', '')}. "
            f"{excerpt_hint}"
        ).strip()
