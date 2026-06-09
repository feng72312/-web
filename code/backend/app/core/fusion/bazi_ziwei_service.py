from __future__ import annotations

from typing import Any

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.interpret_style import InterpretStyle
from app.core.consensus.engine import ConsensusEngine
from app.core.fusion.bazi_channel import run_bazi_channel
from app.core.fusion.merge_bazi_ziwei import merge_bazi_ziwei_stances
from app.core.fusion.models import ChannelVerdict
from app.core.fusion.paipan_charts import build_ziwei_chart_from_paipan
from app.core.fusion.tarot_channel import run_tarot_channel
from app.core.fusion.ziwei_channel import run_ziwei_channel
from app.core.interpret.service import InterpretService
from app.schemas.paipan import PaipanRequest


class BaziZiweiFusionResult:
    def __init__(
        self,
        question: str,
        preferred_channel: str,
        bazi: ChannelVerdict,
        ziwei: ChannelVerdict,
        tarot: ChannelVerdict | None,
        merged_summary: str,
    ) -> None:
        self.question = question
        self.preferred_channel = preferred_channel
        self.bazi = bazi
        self.ziwei = ziwei
        self.tarot = tarot
        self.merged_summary = merged_summary

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "question": self.question,
            "preferredChannel": self.preferred_channel,
            "bazi": self.bazi.to_dict(),
            "ziwei": self.ziwei.to_dict(),
            "merged": {"summary": self.merged_summary},
        }
        if self.tarot is not None:
            payload["tarot"] = self.tarot.to_dict()
        return payload


class BaziZiweiFusionService:
    DEFAULT_QUESTION = "请论此命主格局与当前运势."

    def __init__(self) -> None:
        self._interpret = InterpretService()
        self._consensus = ConsensusEngine()

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
        include_tarot: bool = True,
    ) -> tuple[BaziZiweiFusionResult, str | None]:
        q = (question or "").strip() or self.DEFAULT_QUESTION
        bazi = await run_bazi_channel(
            bazi_chart,
            q,
            chat,
            preset_excerpts=preset_excerpts,
            model_id=model_id,
            style=style,
        )
        ziwei_chart = build_ziwei_chart_from_paipan(body, q)
        ziwei = await run_ziwei_channel(
            ziwei_chart, q, chat, model_id=model_id, style=style
        )

        tarot: ChannelVerdict | None = None
        if include_tarot and settings.fusion_tarot_enabled:
            tarot, _ = await run_tarot_channel(
                q, chat, model_id=model_id, style=style
            )

        preferred = merge_bazi_ziwei_stances(bazi.stance, ziwei.stance, q)
        merged = self._build_merged(q, bazi, ziwei, tarot, preferred)
        result = BaziZiweiFusionResult(
            question=q,
            preferred_channel=preferred,
            bazi=bazi,
            ziwei=ziwei,
            tarot=tarot,
            merged_summary=merged,
        )
        return result, None

    def _build_merged(
        self,
        question: str,
        bazi: ChannelVerdict,
        ziwei: ChannelVerdict,
        tarot: ChannelVerdict | None,
        preferred: str,
    ) -> str:
        parts = [
            f"【综合·命盘级】{question}",
            f"八字({bazi.stance}): {bazi.summary}",
            f"紫微({ziwei.stance}): {ziwei.summary}",
        ]
        if tarot and tarot.available:
            parts.append(f"塔罗({tarot.stance}): {tarot.summary}")
        parts.append(f"主通道: {preferred}")
        return "\n".join(parts)

    def build_interpretation_payload(
        self,
        chart: dict[str, Any],
        fusion: BaziZiweiFusionResult,
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
        base["baziZiweiFusion"] = fusion.to_dict()

        chart_channels = [fusion.bazi, fusion.ziwei]
        if fusion.tarot and fusion.tarot.available:
            chart_consensus = self._consensus.from_chart_channels(
                fusion.question,
                chart_channels,
                lead_discipline=fusion.preferred_channel,
                merged_summary=fusion.merged_summary,
            )
            q_consensus = self._consensus.from_question_channels(
                fusion.question,
                [fusion.tarot],
                lead_discipline="tarot",
                merged_summary=fusion.tarot.summary,
            )
            base["consensus"] = chart_consensus.to_dict()
            base["questionConsensus"] = q_consensus.to_dict()
            base["confidenceBand"] = chart_consensus.confidence_band
            base["confidenceScore"] = chart_consensus.confidence_score
        else:
            consensus = self._consensus.from_chart_channels(
                fusion.question,
                chart_channels,
                lead_discipline=fusion.preferred_channel,
                merged_summary=fusion.merged_summary,
            )
            base = self._consensus.enrich_interpretation(base, consensus)
        return base
