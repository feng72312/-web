from __future__ import annotations

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
            f"请从滴天髓角度分析格局、体用与用神倾向。"
        )

    def build_response(
        self,
        chart: PaipanResult | dict[str, Any],
        excerpts: list[dict[str, str]],
    ) -> dict[str, Any]:
        chart_dict = chart.to_dict() if isinstance(chart, PaipanResult) else chart
        query = self.build_query(chart_dict)
        return {
            "query": query,
            "excerpts": excerpts,
            "summary": self._fallback_summary(chart_dict, excerpts),
        }

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
            rag_note = "当前为演示模式，待接入滴天髓知识库后可生成典籍依据解读。"
        return (
            f"{name_part}日主为{dm}({wx})。{wuxing_note}"
            f"建议结合大运与流年再细看喜忌与应期。{rag_note}"
        )
