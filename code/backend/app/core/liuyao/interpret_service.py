from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class LiuyaoInterpretService:
    RAG_CATEGORY = "02六爻卜筮"

    def build_query(
        self,
        chart: dict[str, Any],
        yong_shen: dict[str, Any],
        question: str | None = None,
    ) -> str:
        ben_name = chart.get("benGua", {}).get("name", "")
        ys = yong_shen.get("yongShen", "")
        moving = chart.get("movingLines", [])
        moving_text = "、".join(str(item) for item in moving) if moving else "无"
        q = question or chart.get("input", {}).get("question", "")
        keywords = self._extract_keywords(q)
        keyword_text = " ".join(keywords) if keywords else q[:40]
        return f"{ben_name} {ys}爻 动爻{moving_text} {keyword_text}"

    def chart_key(self, chart: dict[str, Any]) -> str:
        payload = {
            "benGua": chart.get("benGua", {}).get("name"),
            "movingLines": chart.get("movingLines"),
            "lineValues": chart.get("meta", {}).get("lineValues"),
            "question": chart.get("input", {}).get("question"),
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def build_response(
        self,
        chart: dict[str, Any],
        yong_shen: dict[str, Any],
        excerpts: list[dict[str, str]],
        summary: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        query = self.build_query(chart, yong_shen)
        payload: dict[str, Any] = {
            "query": query,
            "yongShen": yong_shen,
            "excerpts": excerpts,
            "summary": summary or self._fallback_summary(chart, yong_shen, excerpts),
        }
        if agent_id:
            payload["agentId"] = agent_id
        return payload

    def _extract_keywords(self, question: str) -> list[str]:
        tokens = re.findall(r"[\u4e00-\u9fff]{2,}", question)
        stop = {"什么", "怎么", "是否", "能不能", "可以", "这次", "请问"}
        return [token for token in tokens if token not in stop][:5]

    def _fallback_summary(
        self,
        chart: dict[str, Any],
        yong_shen: dict[str, Any],
        excerpts: list[dict[str, str]],
    ) -> str:
        ben = chart.get("benGua", {}).get("name", "")
        ys = yong_shen.get("yongShen", "")
        pos = yong_shen.get("position", "")
        moving = chart.get("movingLines", [])
        note = "已参考典籍摘录." if excerpts else "当前为演示模式."
        return (
            f"本卦以{ys}爻为用神(第{pos}爻). "
            f"本卦{ben}, 动爻{moving or '无'}. "
            f"请结合月建{chart.get('monthJian', '')}与日辰{chart.get('dayChen', '')}再详断. {note}"
        )
