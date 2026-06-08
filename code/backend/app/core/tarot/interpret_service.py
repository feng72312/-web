from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class TarotInterpretService:
    RAG_CATEGORY = "13塔罗占卜"

    def build_query(self, reading: dict[str, Any], question: str | None = None) -> str:
        q = question or reading.get("input", {}).get("question", "")
        deck = reading.get("deckName") or reading.get("deck", "")
        spread = reading.get("spreadName") or reading.get("spreadId", "")
        cards = reading.get("cards") or []
        card_bits: list[str] = []
        for card in cards:
            orient = "逆位" if card.get("orientation") == "reversed" else "正位"
            card_bits.append(f"{card.get('nameZh', '')}{orient}")
        keywords = self._extract_keywords(q)
        keyword_text = " ".join(keywords) if keywords else q[:40]
        return f"{deck} {spread} {' '.join(card_bits)} {keyword_text}".strip()

    def reading_key(self, reading: dict[str, Any]) -> str:
        payload = {
            "deck": reading.get("deck"),
            "spreadId": reading.get("spreadId"),
            "cards": [
                {
                    "cardId": c.get("cardId"),
                    "orientation": c.get("orientation"),
                    "position": c.get("position"),
                }
                for c in reading.get("cards") or []
            ],
            "question": reading.get("input", {}).get("question"),
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def build_response(
        self,
        reading: dict[str, Any],
        excerpts: list[dict[str, str]],
        summary: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        query = self.build_query(reading)
        payload: dict[str, Any] = {
            "query": query,
            "excerpts": excerpts,
            "summary": summary or self._fallback_summary(reading, excerpts),
        }
        if agent_id:
            payload["agentId"] = agent_id
        return payload

    def _extract_keywords(self, question: str) -> list[str]:
        tokens = re.findall(r"[\u4e00-\u9fff]{2,}", question)
        stop = {"什么", "怎么", "是否", "能不能", "可以", "这次", "请问", "塔罗"}
        return [token for token in tokens if token not in stop][:5]

    def _fallback_summary(
        self,
        reading: dict[str, Any],
        excerpts: list[dict[str, str]],
    ) -> str:
        cards = reading.get("cards") or []
        spread = reading.get("spreadName") or reading.get("spreadId", "")
        deck = reading.get("deckName") or reading.get("deck", "")
        lines = [f"牌阵: {spread} ({deck})."]
        for card in cards:
            orient = "逆位" if card.get("orientation") == "reversed" else "正位"
            lines.append(
                f"{card.get('positionLabel', '')}: {card.get('nameZh', '')} ({orient}) - "
                f"{(card.get('meaningZh') or '')[:80]}"
            )
        note = "已参考典籍摘录." if excerpts else "当前为演示模式 (无 AI 或未配置 RAG)."
        lines.append(note)
        return " ".join(lines)
