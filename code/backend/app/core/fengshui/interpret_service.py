from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class FengshuiInterpretService:
    RAG_CATEGORY = "06风水堪舆"

    def build_query(self, chart: dict[str, Any], question: str | None = None) -> str:
        inp = chart.get("input", {})
        method = inp.get("method", "bazhai")
        q = question or inp.get("question", "")
        keywords = self._extract_keywords(q)
        keyword_text = " ".join(keywords) if keywords else q[:40]
        scene = inp.get("scene", "residence")
        scene_label = {"residence": "住宅", "shop": "店铺", "office": "办公室"}.get(
            scene, scene
        )

        if method == "xuankong":
            xk = chart.get("xuankong") or {}
            period = xk.get("period") or {}
            stars = " ".join(
                row.get("label", "")
                for row in (xk.get("combinedPan") or [])[:5]
            )
            return (
                f"玄空飞星 {period.get('label', '')} {xk.get('label', '')} "
                f"山星{xk.get('shanFly', '')} 向星{xk.get('xiangFly', '')} "
                f"{scene_label} {stars} {keyword_text}"
            )

        ming = chart.get("mingGua", {})
        zhai = chart.get("zhaiGua", {})
        ji = " ".join(
            f"{row.get('label', '')}{row.get('direction', '')}"
            for row in chart.get("directions", [])
            if row.get("auspicious")
        )
        xiong = " ".join(
            f"{row.get('label', '')}{row.get('direction', '')}"
            for row in chart.get("directions", [])
            if not row.get("auspicious")
        )
        return (
            f"八宅 {ming.get('groupLabel', '')} {zhai.get('groupLabel', '')} "
            f"{zhai.get('label', '')} {scene_label} "
            f"吉方{ji} 凶方{xiong} {keyword_text}"
        )

    def chart_key(self, chart: dict[str, Any]) -> str:
        inp = chart.get("input", {})
        payload = {
            "method": inp.get("method"),
            "birthYear": inp.get("birthYear"),
            "gender": inp.get("gender"),
            "buildYear": inp.get("buildYear"),
            "flowYear": inp.get("flowYear"),
            "sittingMountain": inp.get("sittingMountain"),
            "question": inp.get("question"),
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
        return {
            "query": self.build_query(chart),
            "knowledgeHits": knowledge_hits,
            "excerpts": excerpts,
            "summary": summary or "",
            "agentId": agent_id,
        }

    def _extract_keywords(self, text: str) -> list[str]:
        if not text:
            return []
        chunks = re.findall(r"[\u4e00-\u9fff]{2,8}", text)
        stop = {"这个", "那个", "是否", "怎么", "如何", "请问", "可以", "适合"}
        seen: set[str] = set()
        result: list[str] = []
        for chunk in chunks:
            if chunk in stop or chunk in seen:
                continue
            seen.add(chunk)
            result.append(chunk)
            if len(result) >= 6:
                break
        return result
