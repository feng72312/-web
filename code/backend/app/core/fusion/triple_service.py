from __future__ import annotations

from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.fusion.bazi_channel import run_bazi_channel
from app.core.fusion.merge_triple import merge_triple_verdicts
from app.core.fusion.models import ChannelVerdict, QuestionScope
from app.core.fusion.paipan_charts import (
    build_xingming_chart_from_paipan,
    build_ziwei_chart_from_paipan,
)
from app.core.fusion.xingming_channel import run_xingming_channel
from app.core.fusion.ziwei_channel import run_ziwei_channel
from app.core.interpret.service import InterpretService
from app.schemas.paipan import PaipanRequest


class TripleFusionResult:
    def __init__(
        self,
        question: str,
        question_scope: QuestionScope,
        preferred_channel: str,
        bazi: ChannelVerdict,
        ziwei: ChannelVerdict,
        xingming: ChannelVerdict,
        merged_summary: str,
    ) -> None:
        self.question = question
        self.question_scope = question_scope
        self.preferred_channel = preferred_channel
        self.bazi = bazi
        self.ziwei = ziwei
        self.xingming = xingming
        self.merged_summary = merged_summary

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "questionScope": self.question_scope,
            "preferredChannel": self.preferred_channel,
            "bazi": self.bazi.to_dict(),
            "ziwei": self.ziwei.to_dict(),
            "xingming": self.xingming.to_dict(),
            "merged": {"summary": self.merged_summary},
        }


class TripleFusionInterpretService:
    DEFAULT_QUESTION = "\u8bf7\u8bba\u6b64\u547d\u4e3b\u5929\u8c61\u9636\u6bb5\u4e0e\u4eba\u751f\u8f6c\u6298."

    def __init__(self) -> None:
        self._interpret = InterpretService()

    async def run(
        self,
        body: PaipanRequest,
        bazi_chart: dict[str, Any],
        chat: ChatOrchestrator | None,
        *,
        question: str | None = None,
        preset_excerpts: list[dict[str, str]] | None = None,
        model_id: str | None = None,
        style: InterpretStyle = "professional",
    ) -> tuple[TripleFusionResult, str | None]:
        q = (question or "").strip() or self.DEFAULT_QUESTION
        default_scope = settings.fusion_triple_default_scope
        if default_scope not in ("life_outline", "event_detail", "mixed", "stage_turn"):
            default_scope = "stage_turn"

        bazi = await run_bazi_channel(
            bazi_chart,
            q,
            chat,
            preset_excerpts=preset_excerpts,
            model_id=model_id,
            style=style,
        )

        ziwei_chart: dict[str, Any] = {}
        xingming_chart: dict[str, Any] = {}
        ziwei = ChannelVerdict(
            channel="ziwei", summary="", stance="", available=False, error=""
        )
        xingming = ChannelVerdict(
            channel="xingming", summary="", stance="", available=False, error=""
        )

        try:
            ziwei_chart = build_ziwei_chart_from_paipan(body, q)
            ziwei = await run_ziwei_channel(
                ziwei_chart, q, chat, model_id=model_id, style=style
            )
        except Exception as err:
            ziwei = ChannelVerdict(
                channel="ziwei",
                summary="",
                stance="",
                available=False,
                error=str(err),
            )

        if settings.fusion_xingming_enabled:
            try:
                xingming_chart = build_xingming_chart_from_paipan(body, q)
                cross = {"baziChart": bazi_chart, "ziweiChart": ziwei_chart}
                xingming = await run_xingming_channel(
                    xingming_chart,
                    q,
                    chat,
                    model_id=model_id,
                    style=style,
                    cross_charts=cross,
                )
            except Exception as err:
                xingming = ChannelVerdict(
                    channel="xingming",
                    summary="",
                    stance="",
                    available=False,
                    error=str(err),
                )

        merged, scope, preferred = merge_triple_verdicts(
            q,
            bazi,
            ziwei,
            xingming,
            default_scope=default_scope,  # type: ignore[arg-type]
        )
        result = TripleFusionResult(
            question=q,
            question_scope=scope,  # type: ignore[arg-type]
            preferred_channel=preferred,
            bazi=bazi,
            ziwei=ziwei,
            xingming=xingming,
            merged_summary=merged,
        )
        return result, None

    def build_interpretation_payload(
        self,
        chart: dict[str, Any],
        fusion: TripleFusionResult,
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
        base["tripleFusion"] = fusion.to_dict()
        return base
