from __future__ import annotations

from typing import Any

from app.config import settings
from app.core.hepan.scene import SCENE_LABELS


class HepanInterpretService:
    def rag_category(self, discipline: str) -> str:
        if discipline == "ziwei":
            return settings.ziwei_rag_category
        return settings.rag_default_category

    def build_query(self, hepan: dict[str, Any], question: str) -> str:
        scene = hepan.get("scene", "")
        discipline = hepan.get("discipline", "")
        tags = " ".join(hepan.get("summaryTags") or [])
        person_a = hepan.get("personA") or {}
        person_b = hepan.get("personB") or {}
        bazi_a = person_a.get("baziChart") or {}
        bazi_b = person_b.get("baziChart") or {}
        dm_a = bazi_a.get("dayMaster", "")
        dm_b = bazi_b.get("dayMaster", "")
        scene_label = SCENE_LABELS.get(scene, scene)
        parts = [
            f"{scene_label}\u5408\u76d8",
            discipline,
            f"\u7532{dm_a}",
            f"\u4e59{dm_b}",
            tags,
            question.strip(),
        ]
        return " ".join(p for p in parts if p).strip()

    def build_response(
        self,
        hepan: dict[str, Any],
        knowledge_hits: list[dict[str, Any]],
        excerpts: list[dict[str, str]],
        summary: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        query = self.build_query(hepan, hepan.get("question") or "")
        return {
            "query": query,
            "knowledgeHits": knowledge_hits,
            "excerpts": excerpts,
            "summary": summary,
            "agentId": agent_id,
        }
