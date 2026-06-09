from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ConfidenceBand = Literal["strong", "medium", "weak"]
FusionMode = Literal["chart", "question", "mixed"]


@dataclass
class ConsensusResult:
    question: str
    fusion_mode: FusionMode
    lead_discipline: str
    confidence_score: float
    confidence_band: ConfidenceBand
    consensus_points: list[str] = field(default_factory=list)
    conflict_points: list[str] = field(default_factory=list)
    conflict_explanation: str = ""
    channels: list[dict[str, Any]] = field(default_factory=list)
    merged_summary: str = ""
    scope: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "fusionMode": self.fusion_mode,
            "leadDiscipline": self.lead_discipline,
            "confidenceScore": self.confidence_score,
            "confidenceBand": self.confidence_band,
            "consensusPoints": self.consensus_points,
            "conflictPoints": self.conflict_points,
            "conflictExplanation": self.conflict_explanation,
            "channels": self.channels,
            "merged": {"summary": self.merged_summary},
            "scope": self.scope,
        }


@dataclass
class UnifiedInterpretExtras:
    """Fields added to interpretation payloads across modules."""

    consensus: ConsensusResult | None = None
    risk_tips: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.consensus is not None:
            payload["consensus"] = self.consensus.to_dict()
        if self.risk_tips:
            payload["riskTips"] = self.risk_tips
        if self.action_items:
            payload["actionItems"] = self.action_items
        return payload
