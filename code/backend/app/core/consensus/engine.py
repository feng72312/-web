from __future__ import annotations

from typing import Any

from app.core.consensus.confidence import compute_confidence
from app.core.consensus.schema import ConfidenceBand, ConsensusResult, FusionMode
from app.core.fusion.models import ChannelVerdict


def _stance_key(channel: ChannelVerdict) -> str:
    s = (channel.stance or "").strip()
    return s if s and s != "未定" else ""


def build_consensus_from_channels(
    question: str,
    channels: list[ChannelVerdict],
    *,
    fusion_mode: FusionMode,
    lead_discipline: str,
    merged_summary: str = "",
    scope: str = "",
    conflict_explanation: str = "",
) -> ConsensusResult:
    available = [c for c in channels if c.available]
    score, band = compute_confidence(channels, lead_available=bool(available))

    stance_groups: dict[str, list[str]] = {}
    for ch in available:
        key = _stance_key(ch)
        if not key:
            continue
        stance_groups.setdefault(key, []).append(ch.channel)

    consensus_points: list[str] = []
    conflict_points: list[str] = []

    if len(stance_groups) == 1:
        only_stance = next(iter(stance_groups))
        names = ", ".join(stance_groups[only_stance])
        consensus_points.append(f"多通道倾向一致: {only_stance} ({names})")
    elif len(stance_groups) > 1:
        for stance, names in stance_groups.items():
            conflict_points.append(f"{', '.join(names)} 倾向 {stance}")
        if not conflict_explanation:
            conflict_explanation = (
                f"通道判断不一致, 本次以 {lead_discipline} 为主通道综合结论."
            )

    for ch in available:
        if ch.summary and ch.channel == lead_discipline:
            consensus_points.append(f"主通道({ch.channel}): {ch.summary[:120]}")

    return ConsensusResult(
        question=question,
        fusion_mode=fusion_mode,
        lead_discipline=lead_discipline,
        confidence_score=score,
        confidence_band=band,
        consensus_points=consensus_points,
        conflict_points=conflict_points,
        conflict_explanation=conflict_explanation,
        channels=[c.to_dict() for c in channels],
        merged_summary=merged_summary,
        scope=scope,
    )


class ConsensusEngine:
    """Facade for chart-level and question-level consensus."""

    def from_chart_channels(
        self,
        question: str,
        channels: list[ChannelVerdict],
        *,
        lead_discipline: str,
        merged_summary: str = "",
        scope: str = "",
    ) -> ConsensusResult:
        return build_consensus_from_channels(
            question,
            channels,
            fusion_mode="chart",
            lead_discipline=lead_discipline,
            merged_summary=merged_summary,
            scope=scope,
        )

    def from_question_channels(
        self,
        question: str,
        channels: list[ChannelVerdict],
        *,
        lead_discipline: str,
        merged_summary: str = "",
    ) -> ConsensusResult:
        return build_consensus_from_channels(
            question,
            channels,
            fusion_mode="question",
            lead_discipline=lead_discipline,
            merged_summary=merged_summary,
        )

    def enrich_interpretation(
        self,
        interpretation: dict[str, Any],
        consensus: ConsensusResult,
    ) -> dict[str, Any]:
        out = dict(interpretation)
        out["consensus"] = consensus.to_dict()
        out["confidenceBand"] = consensus.confidence_band
        out["confidenceScore"] = consensus.confidence_score
        return out
