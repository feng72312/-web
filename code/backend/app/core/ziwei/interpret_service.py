from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class ZiweiInterpretService:
    RAG_CATEGORY = "11紫微斗数"

    def build_query(self, chart: dict[str, Any], question: str | None = None) -> str:
        inp = chart.get("input") or {}
        q = (question or inp.get("question") or "").strip()
        keywords = self._extract_keywords(q)
        kw = " ".join(keywords) if keywords else q[:40]
        meta = chart.get("meta") or {}
        soul = chart.get("palaces") or []
        soul_palace = soul[0] if soul else {}
        major = " ".join(s.get("name", "") for s in soul_palace.get("majorStars") or [])
        limits = chart.get("limits") or {}
        yearly = limits.get("yearly") or {}
        parts = [
            meta.get("bureau", ""),
            f"命宫{major}",
            meta.get("soul", ""),
            meta.get("body", ""),
            f"流年{yearly.get('heavenlyStem', '')}{yearly.get('earthlyBranch', '')}",
            kw,
        ]
        return " ".join(p for p in parts if p).strip()

    def chart_key(self, chart: dict[str, Any]) -> str:
        payload = {
            "trueSolarTime": chart.get("trueSolarTime"),
            "fourPillars": chart.get("fourPillars"),
            "bureau": (chart.get("meta") or {}).get("bureau"),
            "rulesMeta": chart.get("rulesMeta"),
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
        payload: dict[str, Any] = {
            "query": self.build_query(chart),
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
        return [t for t in tokens if t not in stop][:5]

    def _fallback_summary(self, chart: dict[str, Any], excerpts: list[dict[str, str]]) -> str:
        meta = chart.get("meta") or {}
        palaces = chart.get("palaces") or []
        soul = palaces[0] if palaces else {}
        major = "、".join(s.get("name", "") for s in soul.get("majorStars") or [])
        hint = excerpts[0].get("excerpt", "")[:80] if excerpts else ""
        return (
            f"{meta.get('bureau', '')} 命宫主星{major or '未入主星'}. "
            f"命主{meta.get('soul', '')} 身主{meta.get('body', '')}. {hint}"
        ).strip()
