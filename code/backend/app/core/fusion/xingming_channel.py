from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.agent.prompts_xingming import build_xingming_interpret_prompt
from app.core.fusion.models import ChannelVerdict
from app.core.fusion.text_util import strip_stance_line
from app.core.knowledge.factory import get_knowledge_service
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.xingming.case_store import search_cases
from app.core.xingming.interpret_service import XingmingInterpretService

logger = logging.getLogger(__name__)


async def run_xingming_channel(
    chart: dict[str, Any],
    question: str,
    chat: ChatOrchestrator | None,
    *,
    model_id: str | None = None,
    style: InterpretStyle = "professional",
    cross_charts: dict[str, Any] | None = None,
) -> ChannelVerdict:
    interpret = XingmingInterpretService()
    query = interpret.build_query(chart, question)
    knowledge_hits: list[dict[str, Any]] = []
    excerpts: list[dict[str, str]] = []
    cases = search_cases(
        chart,
        question,
        tier="gold" if settings.xingming_case_gold_only else None,
        top_k=5,
    )

    knowledge = get_knowledge_service()
    if knowledge.enabled:
        try:
            resolved = knowledge.resolve_for_xingming(chart)
            knowledge_hits = [h.model_dump() for h in resolved.hits]
        except Exception as err:
            logger.warning("xingming knowledge: %s", err)

    if settings.rag_provider == "http" and settings.rag_http_url:
        try:
            rag = build_rag_provider()
            excerpts = normalize_rag_excerpts(
                await rag.search(query, category=settings.xingming_rag_category)
            )
        except Exception as err:
            logger.warning("xingming channel rag: %s", err)

    summary = None
    stance = "\u672a\u5b9a"
    if chat is not None and chat.enabled:
        prompt = build_xingming_interpret_prompt(
            chart,
            knowledge_hits,
            excerpts,
            cases,
            cross_charts=cross_charts,
            style=style,
        )
        try:
            summary, _ = await chat.interpret(prompt, model_id)
            if summary:
                stance = strip_stance_line(summary) or "\u5929\u8c61"
        except Exception as err:
            logger.warning("xingming channel ai: %s", err)
            return ChannelVerdict(
                channel="xingming",
                summary="",
                stance="",
                available=False,
                error=str(err),
                query=query,
                excerpts=excerpts,
            )

    if not summary:
        ming = chart.get("mingPalace") or {}
        major = "\u3001".join(s.get("label", "") for s in ming.get("majorStars") or [])
        no_star = "\u65e0"
        summary = (
            f"\u547d\u5bab{ming.get('branch', '')} "
            f"\u4e3b\u661f{major or no_star}; "
            f"\u592a\u5c81{(chart.get('limits') or {}).get('taiSui', {}).get('branch', '')}."
        )
        stance = "\u5929\u8c61"

    return ChannelVerdict(
        channel="xingming",
        summary=summary,
        stance=stance,
        available=True,
        query=query,
        excerpts=excerpts,
        extra={"cases": cases},
    )
