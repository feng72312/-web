from __future__ import annotations

import hashlib
import json
from typing import Any

from app.core.paipan.models import PaipanResult


class InterpretService:
    """Compose RAG queries from structured chart data."""

    def build_query(self, chart: dict[str, Any]) -> str:
        dm = chart["dayMaster"]
        dm_wx = chart["dayMasterWuxing"]
        month = chart["pillars"]["month"]
        month_pillar = month["ganzhi"]
        shishen = chart["pillars"]["month"]["shishenGan"]
        return (
            f"日主{dm}{dm_wx}生于{month_pillar}月，"
            f"月干十神为{shishen}，"
            f"请从八字命理典籍中检索格局、体用、用神、喜忌与调候相关论述。"
        )

    def chart_key(self, chart: dict[str, Any]) -> str:
        inp = chart.get("input", {})
        payload = {
            "calendarType": inp.get("calendarType"),
            "year": inp.get("year"),
            "month": inp.get("month"),
            "day": inp.get("day"),
            "hour": inp.get("hour"),
            "minute": inp.get("minute"),
            "gender": inp.get("gender"),
            "isLeapMonth": inp.get("isLeapMonth"),
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def build_response(
        self,
        chart: PaipanResult | dict[str, Any],
        excerpts: list[dict[str, str]],
        summary: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        chart_dict = chart.to_dict() if isinstance(chart, PaipanResult) else chart
        query = self.build_query(chart_dict)
        payload: dict[str, Any] = {
            "query": query,
            "excerpts": excerpts,
            "summary": summary or self._fallback_summary(chart_dict, excerpts),
        }
        if agent_id:
            payload["agentId"] = agent_id
        return payload

    def _fallback_summary(
        self, chart: dict[str, Any], excerpts: list[dict[str, str]]
    ) -> str:
        dm = chart["dayMaster"]
        wx = chart["dayMasterWuxing"]
        name = chart.get("input", {}).get("name") or ""
        name_part = f"{name}的" if name else ""
        dominant = chart.get("analysis", [{}])
        wuxing_note = ""
        for section in chart.get("sections", []):
            if section.get("id") == "wuxing":
                data = section.get("data", {})
                wuxing_note = (
                    f"五行偏{data.get('dominant', '')}弱{data.get('weakest', '')}。"
                )
                break
        rag_note = ""
        if excerpts and excerpts[0].get("source") != "stub":
            rag_note = "以下参考知识库摘录生成。"
        else:
            rag_note = "当前为演示模式，待接入命理典籍知识库后可生成典籍依据解读。"
        return (
            f"{name_part}日主为{dm}({wx})。{wuxing_note}"
            f"建议结合大运与流年再细看喜忌与应期。{rag_note}"
        )
