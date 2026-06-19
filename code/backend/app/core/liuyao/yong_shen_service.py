from __future__ import annotations

from typing import Any

from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_liuyao import build_yong_shen_prompt
from app.core.liuyao.judgement.topic_judge import classify_topic
from app.core.liuyao.judgement.yong_shen_judge import judge_yong_shen
from app.core.liuyao.models import LIUQIN_NAMES, YongShenResult
from app.core.liuyao.yong_shen_rules import (
    fallback_yong_shen,
    find_yong_shen_position,
    parse_yong_shen_json,
)

__all__ = ["YongShenService", "fallback_yong_shen"]

RULE_CONFIDENCE_THRESHOLD = 0.45


class YongShenService:
    async def infer(
        self,
        chart: dict[str, Any],
        question: str,
        chat: ChatOrchestrator | None,
        model_id: str | None = None,
    ) -> YongShenResult:
        topic = classify_topic(question)
        rule_result = judge_yong_shen(chart, question, topic)
        if rule_result.confidence >= RULE_CONFIDENCE_THRESHOLD:
            return rule_result

        if chat is None or not chat.enabled:
            if rule_result.confidence > 0.3:
                return rule_result
            return fallback_yong_shen(chart, question)

        prompt = build_yong_shen_prompt(chart, question)
        try:
            text, _ = await chat.interpret(prompt, model_id)
        except Exception:
            if rule_result.confidence > 0.3:
                return rule_result
            return fallback_yong_shen(chart, question)

        payload = parse_yong_shen_json(text)
        if not payload:
            if rule_result.confidence > 0.3:
                return rule_result
            return fallback_yong_shen(chart, question)

        yong_shen = str(payload.get("yongShen", "")).strip()
        if yong_shen not in LIUQIN_NAMES:
            if rule_result.confidence > 0.3:
                return rule_result
            return fallback_yong_shen(chart, question)

        position = int(payload.get("position") or find_yong_shen_position(chart, yong_shen))
        if position < 1 or position > 6:
            position = find_yong_shen_position(chart, yong_shen)

        reason = str(payload.get("reason") or "AI 推断").strip()
        return YongShenResult(
            yong_shen=yong_shen,
            position=position,
            reason=reason,
            source="ai",
            confidence=0.55,
            topic_id=topic.topic_id,
        )

    def apply_override(
        self,
        chart: dict[str, Any],
        yong_shen: str,
        position: int | None = None,
    ) -> YongShenResult:
        if yong_shen not in LIUQIN_NAMES:
            raise ValueError("invalid yongShen")
        pos = position or find_yong_shen_position(chart, yong_shen)
        return YongShenResult(
            yong_shen=yong_shen,
            position=pos,
            reason="用户手动指定用神",
            source="manual",
            confidence=1.0,
        )
