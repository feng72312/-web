from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

ConfidenceBand = Literal["strong", "medium", "weak"]
FusionMode = Literal["chart", "question", "mixed"]


class ChannelVerdictOut(BaseModel):
    channel: str
    summary: str = ""
    stance: str = ""
    available: bool = True
    error: str = ""
    query: str = ""


class ConsensusOut(BaseModel):
    question: str = ""
    fusionMode: FusionMode = "chart"
    leadDiscipline: str = ""
    confidenceScore: float = 0.0
    confidenceBand: ConfidenceBand = "weak"
    consensusPoints: list[str] = Field(default_factory=list)
    conflictPoints: list[str] = Field(default_factory=list)
    conflictExplanation: str = ""
    channels: list[dict[str, Any]] = Field(default_factory=list)
    merged: dict[str, str] = Field(default_factory=dict)
    scope: str = ""


class UnifiedInterpretationOut(BaseModel):
    """Canonical interpretation fields across all modules."""

    query: str = ""
    summary: str = ""
    summaryProfessional: Optional[str] = None
    summaryPlain: Optional[str] = None
    excerpts: list[dict[str, str]] = Field(default_factory=list)
    agentId: Optional[str] = None
    confidenceBand: Optional[ConfidenceBand] = None
    confidenceScore: Optional[float] = None
    consensus: Optional[ConsensusOut] = None
    questionConsensus: Optional[ConsensusOut] = None
    riskTips: list[str] = Field(default_factory=list)
    actionItems: list[str] = Field(default_factory=list)
    fusion: Optional[dict[str, Any]] = None
    tripleFusion: Optional[dict[str, Any]] = None
    baziZiweiFusion: Optional[dict[str, Any]] = None
