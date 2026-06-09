from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.agent.prompts_tarot import build_tarot_interpret_prompt
from app.core.fusion.models import ChannelVerdict
from app.core.agent.prompts_fusion import parse_stance
from app.core.rag.factory import build_rag_provider
from app.core.tarot.engine import TarotEngine
from app.core.tarot.interpret_service import TarotInterpretService
from app.core.tarot.models import TarotInput

logger = logging.getLogger(__name__)

_engine = TarotEngine()
_interpret = TarotInterpretService()


async def run_tarot_channel(
    question: str,
    chat: ChatOrchestrator | None,
    *,
    deck: str = "rws",
    spread: str = "three-card",
    model_id: str | None = None,
    style: InterpretStyle = "professional",
) -> tuple[ChannelVerdict, dict[str, Any]]:
    """Question-level tarot channel (no birth chart)."""
    q = (question or "").strip()
    if not q:
        return (
            ChannelVerdict(
                channel="tarot",
                summary="",
                stance="",
                available=False,
                error="empty question",
            ),
            {},
        )
    try:
        reading = _engine.draw(
            TarotInput(question=q, deck=deck, spread=spread, allow_reversed=True)
        ).to_dict()
    except Exception as err:
        logger.warning("tarot channel draw: %s", err)
        return (
            ChannelVerdict(
                channel="tarot",
                summary="",
                stance="",
                available=False,
                error=str(err),
            ),
            {},
        )

    query = _interpret.build_query(reading, q)
    excerpts: list[dict[str, str]] = []
    try:
        rag = build_rag_provider()
        excerpts = await rag.search(query, category=settings.tarot_rag_category)
    except Exception as err:
        logger.warning("tarot channel rag: %s", err)

    summary = ""
    if chat is not None and chat.enabled:
        prompt = build_tarot_interpret_prompt(reading, excerpts, style=style)
        try:
            summary, _ = await chat.interpret(prompt, model_id)
        except Exception as err:
            logger.warning("tarot channel ai: %s", err)

    stance = parse_stance(summary) if summary else "未定"
    return (
        ChannelVerdict(
            channel="tarot",
            summary=summary or "塔罗通道已抽牌, AI 解读未生成.",
            stance=stance,
            available=True,
            query=query,
            excerpts=excerpts,
            extra={"spreadId": spread, "deck": deck},
        ),
        reading,
    )
