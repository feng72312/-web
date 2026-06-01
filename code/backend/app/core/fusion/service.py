from __future__ import annotations

from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.fusion.bazi_channel import run_bazi_channel
from app.core.fusion.liuyao_channel import run_liuyao_channel
from app.core.fusion.merge import merge_verdicts
from app.core.fusion.models import FusionResult
from app.core.interpret.service import InterpretService
from app.schemas.paipan import PaipanRequest


class FusionInterpretService:
    DEFAULT_QUESTION = "请论此命主格局、用神喜忌与一生大势."

    def __init__(self) -> None:
        self._interpret = InterpretService()

    async def run(
        self,
        body: PaipanRequest,
        chart: dict[str, Any],
        chat: ChatOrchestrator | None,
        *,
        question: str | None = None,
        preset_excerpts: list[dict[str, str]] | None = None,
        model_id: str | None = None,
        style: InterpretStyle = "professional",
    ) -> tuple[FusionResult, str | None]:
        q = (question or "").strip() or self.DEFAULT_QUESTION
        default_scope = settings.fusion_default_scope
        if default_scope not in ("life_outline", "event_detail", "mixed"):
            default_scope = "life_outline"

        bazi = await run_bazi_channel(
            chart,
            q,
            chat,
            preset_excerpts=preset_excerpts,
            model_id=model_id,
            style=style,
        )
        liuyao = await run_liuyao_channel(body, q, chat, model_id=model_id, style=style)

        fusion = merge_verdicts(
            q,
            bazi,
            liuyao,
            default_scope=default_scope,
        )

        agent_id: str | None = None
        return fusion, agent_id

    def build_interpretation_payload(
        self,
        chart: dict[str, Any],
        fusion: FusionResult,
        *,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        base = self._interpret.build_response(
            chart,
            fusion.bazi.excerpts,
            summary=fusion.merged_summary,
            agent_id=agent_id,
        )
        base["query"] = fusion.bazi.query or base.get("query", "")
        base["excerpts"] = fusion.bazi.excerpts
        base["summary"] = fusion.merged_summary
        base["fusion"] = fusion.to_dict()
        return base
