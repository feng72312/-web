from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.agent.prompts_ziwei import build_ziwei_interpret_prompt
from app.core.fusion.models import ChannelVerdict
from app.core.agent.prompts_fusion import parse_stance
from app.core.fusion.text_util import strip_stance_line
from app.core.fusion.rag_util import safe_rag_search
from app.core.knowledge.evidence import knowledge_hits_to_evidence
from app.core.knowledge.factory import get_knowledge_service
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
    knowledge_hits: list[dict[str, Any]] = []
    knowledge = get_knowledge_service()
    if knowledge.enabled:
        try:
            resolved = knowledge.resolve_for_ziwei(chart)
            knowledge_hits = [h.model_dump() for h in resolved.hits]
        except Exception as err:
            logger.warning("ziwei knowledge: %s", err)

    warnings: list[str] = []
    if settings.rag_provider == "http" and settings.rag_http_url:
        excerpts, rag_err = await safe_rag_search(
            query, category=settings.ziwei_rag_category
        )
        if rag_err:
            warnings.append(f"典籍检索失败: {rag_err}")

    summary = None
    stance = "\u672a\u5b9a"
    if chat is not None and chat.enabled:
        prompt = build_ziwei_interpret_prompt(chart, [], excerpts, style=style)
        try:
            summary, _ = await chat.interpret(prompt, model_id)
            if summary:
                stance = parse_stance(summary)
                summary = strip_stance_line(summary)
        except Exception as err:
            logger.warning("ziwei channel ai: %s", err)
            warnings.append(f"AI 解读失败: {err}")

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
        error="; ".join(warnings),
        query=query,
        excerpts=excerpts,
        extra={
            "knowledgeHits": len(knowledge_hits),
            "knowledgeEvidence": knowledge_hits_to_evidence(knowledge_hits),
        },
    )
