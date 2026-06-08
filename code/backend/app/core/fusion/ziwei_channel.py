from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.agent.prompts_ziwei import build_ziwei_interpret_prompt
from app.core.fusion.models import ChannelVerdict
from app.core.fusion.text_util import strip_stance_line
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.ziwei.interpret_service import ZiweiInterpretService

logger = logging.getLogger(__name__)


async def run_ziwei_channel(
    chart: dict[str, Any],
    question: str,
    chat: ChatOrchestrator | None,
    *,
    model_id: str | None = None,
    style: InterpretStyle = "professional",
) -> ChannelVerdict:
    interpret = ZiweiInterpretService()
    query = interpret.build_query(chart, question)
    excerpts: list[dict[str, str]] = []

    if settings.rag_provider == "http" and settings.rag_http_url:
        try:
            rag = build_rag_provider()
            excerpts = normalize_rag_excerpts(
                await rag.search(query, category=settings.ziwei_rag_category)
            )
        except Exception as err:
            logger.warning("ziwei channel rag: %s", err)

    summary = None
    stance = "\u672a\u5b9a"
    if chat is not None and chat.enabled:
        prompt = build_ziwei_interpret_prompt(chart, [], excerpts, style=style)
        try:
            summary, _ = await chat.interpret(prompt, model_id)
            if summary:
                stance = strip_stance_line(summary) or "\u7d2b\u5fae"
        except Exception as err:
            logger.warning("ziwei channel ai: %s", err)
            return ChannelVerdict(
                channel="ziwei",
                summary="",
                stance="",
                available=False,
                error=str(err),
                query=query,
                excerpts=excerpts,
            )

    if not summary:
        palaces = chart.get("palaces") or []
        major = ""
        if palaces:
            major = "\u3001".join(
                s.get("name", "") for s in palaces[0].get("majorStars") or []
            )
        no_star = "\u65e0"
        summary = f"\u547d\u5bab\u4e3b\u661f{major or no_star}."
        stance = "\u7d2b\u5fae"

    return ChannelVerdict(
        channel="ziwei",
        summary=summary,
        stance=stance,
        available=True,
        query=query,
        excerpts=excerpts,
    )
