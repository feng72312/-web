from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.agent.prompts_fusion import build_liuyao_channel_prompt, parse_stance
from app.core.fusion.inputs import paipan_to_liuyao_input
from app.core.fusion.models import ChannelVerdict
from app.core.fusion.rag_util import safe_rag_search
from app.core.fusion.text_util import strip_stance_line
from app.core.knowledge.evidence import knowledge_hits_to_evidence
from app.core.knowledge.factory import get_knowledge_service
from app.core.liuyao.engine import LiuyaoEngine
from app.core.liuyao.interpret_service import LiuyaoInterpretService
from app.core.liuyao.yong_shen_service import YongShenService
from app.schemas.paipan import PaipanRequest

logger = logging.getLogger(__name__)

_engine = LiuyaoEngine()
_yong_shen = YongShenService()
_interpret = LiuyaoInterpretService()


async def run_liuyao_channel(
    body: PaipanRequest,
    question: str,
    chat: ChatOrchestrator | None,
    *,
    model_id: str | None = None,
    style: InterpretStyle = "professional",
) -> ChannelVerdict:
    warnings: list[str] = []
    query = ""
    try:
        chart = _engine.divine(paipan_to_liuyao_input(body, question)).to_dict()
        ys_result = await _yong_shen.infer(chart, question, chat, model_id)
        yong_shen = ys_result.to_dict()

        query = _interpret.build_query(chart, yong_shen, question)
        knowledge_hits: list[dict[str, Any]] = []
        knowledge = get_knowledge_service()
        if knowledge.enabled:
            try:
                chart_ctx = {**chart, "yongShen": yong_shen}
                resolved = knowledge.resolve_for_liuyao(chart_ctx)
                knowledge_hits = [h.model_dump() for h in resolved.hits]
            except Exception as err:
                logger.warning("liuyao knowledge: %s", err)

        excerpts: list[dict[str, str]] = []
        if settings.rag_provider == "http" and settings.rag_http_url:
            excerpts, rag_err = await safe_rag_search(
                query, category=settings.liuyao_rag_category
            )
            if rag_err:
                warnings.append(f"典籍检索失败: {rag_err}")

        summary = None
        if chat is not None and chat.enabled:
            prompt = build_liuyao_channel_prompt(
                chart, yong_shen, excerpts, question, style=style
            )
            try:
                summary, _ = await chat.interpret(prompt, model_id)
            except Exception as err:
                logger.warning("liuyao channel ai: %s", err)
                warnings.append(f"AI 解读失败: {err}")

        if not summary:
            payload = _interpret.build_response(chart, yong_shen, excerpts, summary=None)
            summary = payload.get("summary") or "六爻通道暂无 AI 解读."

        stance = parse_stance(summary)
        clean = strip_stance_line(summary)
        ben = chart.get("benGua", {}) or {}
        return ChannelVerdict(
            channel="liuyao",
            summary=clean,
            stance=stance,
            available=True,
            error="; ".join(warnings),
            query=query,
            excerpts=excerpts,
            extra={
                "yongShen": yong_shen,
                "benGuaName": ben.get("name", ""),
                "castNote": chart.get("meta", {}).get("castNote", ""),
                "movingLines": chart.get("movingLines", []),
                "knowledgeHits": len(knowledge_hits),
                "knowledgeEvidence": knowledge_hits_to_evidence(knowledge_hits),
            },
        )
    except Exception as err:
        logger.exception("liuyao channel failed")
        return ChannelVerdict(
            channel="liuyao",
            summary="",
            stance="未定",
            available=False,
            error=str(err),
            query=query,
        )
