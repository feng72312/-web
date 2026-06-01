from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.agent.prompts_fusion import build_bazi_channel_prompt, parse_stance
from app.core.fusion.text_util import strip_stance_line
from app.core.fusion.models import ChannelVerdict
from app.core.interpret.service import InterpretService
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.rag_fallback import fetch_on_demand_rag
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider

logger = logging.getLogger(__name__)


async def run_bazi_channel(
    chart: dict[str, Any],
    question: str,
    chat: ChatOrchestrator | None,
    *,
    preset_excerpts: list[dict[str, str]] | None = None,
    model_id: str | None = None,
    style: InterpretStyle = "professional",
) -> ChannelVerdict:
    interpret_service = InterpretService()
    query = interpret_service.build_query(chart)
    knowledge = get_knowledge_service()
    compressed = None
    excerpts: list[dict[str, str]] = []

    try:
        if preset_excerpts is not None:
            excerpts = normalize_rag_excerpts(preset_excerpts)
        elif settings.knowledge_use_legacy_rag_first or not knowledge.enabled:
            rag = build_rag_provider()
            excerpts = normalize_rag_excerpts(
                await rag.search(query, category=settings.rag_default_category)
            )
        else:
            compressed = knowledge.resolve_for_chart(chart)
            if settings.knowledge_rag_fallback and compressed.missingTopics:
                rag = build_rag_provider()
                try:
                    excerpts = normalize_rag_excerpts(
                        await fetch_on_demand_rag(
                            rag,
                            chart,
                            compressed.missingTopics,
                            category=settings.rag_default_category,
                        )
                    )
                except Exception as err:
                    logger.warning("bazi channel rag fallback: %s", err)

        summary = None
        if (
            settings.knowledge_direct_answer_enabled
            and compressed is not None
            and compressed.directAnswer
            and not settings.knowledge_use_legacy_rag_first
        ):
            summary = compressed.directAnswer

        if summary is None and chat is not None and chat.enabled:
            prompt = build_bazi_channel_prompt(
                chart,
                question,
                compressed=compressed,
                rag_excerpts=excerpts,
                style=style,
            )
            summary, _ = await chat.interpret(prompt, model_id)

        if not summary:
            payload = interpret_service.build_response(chart, excerpts, summary=None)
            summary = payload.get("summary") or "八字通道暂无 AI 解读."

        stance = parse_stance(summary)
        clean = strip_stance_line(summary)
        return ChannelVerdict(
            channel="bazi",
            summary=clean,
            stance=stance,
            available=True,
            query=query,
            excerpts=excerpts,
            extra={"knowledgeHits": len(compressed.hits) if compressed else 0},
        )
    except Exception as err:
        logger.exception("bazi channel failed")
        return ChannelVerdict(
            channel="bazi",
            summary="",
            stance="未定",
            available=False,
            error=str(err),
            query=query,
        )
