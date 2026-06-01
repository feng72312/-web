from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class MeihuaInterpretService:
    RAG_CATEGORY = "03梅花易学"

    def build_query(self, chart: dict[str, Any], question: str | None = None) -> str:
        ben = chart.get("benGua", {})
        ti = chart.get("tiGua", {})
        yong = chart.get("yongGua", {})
        moving = chart.get("movingLines", [])
        moving_text = "、".join(str(item) for item in moving) if moving else "静卦"
        q = question or chart.get("input", {}).get("question", "")
        keywords = self._extract_keywords(q)
        keyword_text = " ".join(keywords) if keywords else q[:40]
        return (
            f"{ben.get('name', '')} 体{ti.get('name', '')}({ti.get('element', '')}) "
            f"用{yong.get('name', '')}({yong.get('element', '')}) "
            f"{chart.get('tiYongRelation', '')} 动爻{moving_text} {keyword_text}"
        )

    def chart_key(self, chart: dict[str, Any]) -> str:
        payload = {
            "benGua": chart.get("benGua", {}).get("name"),
            "movingLines": chart.get("movingLines"),
            "lineValues": chart.get("meta", {}).get("lineValues"),
            "tiGua": chart.get("tiGua", {}).get("name"),
            "yongGua": chart.get("yongGua", {}).get("name"),
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
        ti = chart.get("tiGua", {})
        yong = chart.get("yongGua", {})
        payload: dict[str, Any] = {
            "query": self.build_query(chart),
            "tiYong": {
                "tiGua": ti,
                "yongGua": yong,
                "relation": chart.get("tiYongRelation", ""),
                "isStatic": chart.get("isStatic", False),
            },
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
        ben = chart.get("benGua", {}).get("name", "")
        ti = chart.get("tiGua", {})
        yong = chart.get("yongGua", {})
        rel = chart.get("tiYongRelation", "")
        excerpt_hint = excerpts[0].get("excerpt", "")[:80] if excerpts else ""
        base = (
            f"本卦{ben}, 体卦{ti.get('name', '')}({ti.get('element', '')}), "
            f"用卦{yong.get('name', '')}({yong.get('element', '')}), 关系{rel}."
        )
        if excerpt_hint:
            return f"{base} 典籍摘录: {excerpt_hint}"
        return base
