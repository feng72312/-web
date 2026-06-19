from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ConfidenceBand = Literal["strong", "medium", "weak"]
ZiweiJudgeRole = Literal[
    "topic",
    "palace",
    "star",
    "mutagen",
    "pattern",
    "limit",
    "cross_school",
]
StepStatus = Literal["pending", "ok", "partial", "skipped"]
ConclusionKind = Literal[
    "classic_direct",
    "rule_derived",
    "experience_reference",
    "insufficient_evidence",
]
Stance = Literal["favorable", "unfavorable", "neutral", "mixed"]


class JudgementStep(BaseModel):
    id: str
    label: str
    status: StepStatus = "pending"
    summary: str = ""


class EvidenceRequest(BaseModel):
    ruleId: str = ""
    topic: str = ""
    sourceScope: list[str] = Field(default_factory=list)
    libraryRoles: list[str] = Field(default_factory=list)
    classicWhitelist: list[str] = Field(default_factory=list)
    authorityTiers: list[str] = Field(default_factory=lambda: ["S", "A"])
    evidenceRoles: list[str] = Field(default_factory=list)
    palaceScope: list[str] = Field(default_factory=list)
    starScope: list[str] = Field(default_factory=list)
    school: str = "general"
    query: str = ""
    judgeOnly: bool = False


class ZiweiJudgeVerdict(BaseModel):
    role: ZiweiJudgeRole
    classic: str = ""
    summary: str = ""
    stance: Stance = "neutral"
    ruleIds: list[str] = Field(default_factory=list)
    confidenceBand: ConfidenceBand = "medium"
    conclusionKind: ConclusionKind = "rule_derived"
    boundary: str = ""
    flags: dict[str, Any] = Field(default_factory=dict)


class EvidenceChainItem(BaseModel):
    conclusion: str
    ruleId: str = ""
    primaryClassic: str = ""
    quote: str = ""
    secondary: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    boundary: str = ""
    confidence: ConfidenceBand = "medium"
    conclusionKind: ConclusionKind = "rule_derived"


class ArbitrationResult(BaseModel):
    judgeOpinions: list[ZiweiJudgeVerdict] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    finalBoundaries: list[str] = Field(default_factory=list)
    confidenceScore: float = 0.5
    confidenceBand: ConfidenceBand = "medium"
    evidenceRequests: list[EvidenceRequest] = Field(default_factory=list)
    summary: str = ""


class TieredEvidence(BaseModel):
    primaryEvidence: list[dict[str, Any]] = Field(default_factory=list)
    secondaryEvidence: list[dict[str, Any]] = Field(default_factory=list)
    schoolCommentary: list[dict[str, Any]] = Field(default_factory=list)
    caseReference: list[dict[str, Any]] = Field(default_factory=list)
    excludedOrUnreadable: list[dict[str, Any]] = Field(default_factory=list)


class ZiweiJudgementReport(BaseModel):
    steps: list[JudgementStep] = Field(default_factory=list)
    topic: dict[str, Any] = Field(default_factory=dict)
    judges: list[ZiweiJudgeVerdict] = Field(default_factory=list)
    arbitration: ArbitrationResult = Field(default_factory=ArbitrationResult)
    evidenceChain: list[EvidenceChainItem] = Field(default_factory=list)
    tieredEvidence: TieredEvidence = Field(default_factory=TieredEvidence)
    tieredEvidenceSummary: dict[str, Any] = Field(default_factory=dict)
    enrichedChart: dict[str, Any] = Field(default_factory=dict)
    rulesMeta: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
