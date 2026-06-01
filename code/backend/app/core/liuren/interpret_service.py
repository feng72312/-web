from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class LiurenInterpretService:
    RAG_CATEGORY = "05大六壬"

    def build_query(self, chart: dict[str, Any], question: str | None = None) -> str:
        inp = chart.get("input", {})
        q = question or inp.get("question", "")
        keywords = self._extract_keywords(q)
        kw = " ".join(keywords) if keywords else q[:40]
        parts = []
        lr = chart.get("liuren")
        if lr:
            ge = lr.get("geJu", {})
            sc = lr.get("sanChuan", {})
            parts.append(
                f"{lr.get('jieqi', '')} {lr.get('yueJiang', '')} "
                f"{ge.get('name', '')}{ge.get('sub', '')} "
                f"初传{sc.get('chu', {}).get('zhi', '')} "
                f"{sc.get('chu', {}).get('general', '')}"
            )
        jk = chart.get("jinkou")
        if jk:
            parts.append(f"金口诀人元{jk.get('renYuan', '')} 地分{jk.get('difen', '')}")
        cat = "事占" if inp.get("category") == "shizhan" else "行占"
        return f"{cat} {' '.join(parts)} {kw}".strip()

    def chart_key(self, chart: dict[str, Any]) -> str:
        lr = chart.get("liuren") or {}
        payload = {
            "trueSolarTime": chart.get("trueSolarTime"),
            "geJu": lr.get("geJu"),
            "fourPillars": lr.get("fourPillars") or chart.get("jinkou", {}).get("fourPillars"),
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
        lr = chart.get("liuren") or {}
        ge = lr.get("geJu", {})
        hint = excerpts[0].get("excerpt", "")[:80] if excerpts else ""
        return (
            f"{lr.get('jieqi', '')} {ge.get('name', '')}{ge.get('sub', '')} "
            f"月将{lr.get('yueJiang', '')}. {hint}"
        ).strip()
