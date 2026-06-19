from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.liuyao.judgement.models import TopicResult

ConfidenceBand = Literal["strong", "medium", "weak"]
LiuyaoJudgeRole = Literal[
    "topic",
    "yong_shen",
    "wang_shuai",
    "sheng_ke",
    "dong_bian",
    "shi_ying",
    "liu_shen",
    "ying_qi",
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
    query: str = ""
    judgeOnly: bool = False


class LiuyaoJudgeVerdict(BaseModel):
    role: LiuyaoJudgeRole
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
    judgeOpinions: list[LiuyaoJudgeVerdict] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    finalBoundaries: list[str] = Field(default_factory=list)
    confidenceScore: float = 0.5
    confidenceBand: ConfidenceBand = "medium"
    evidenceRequests: list[EvidenceRequest] = Field(default_factory=list)
    summary: str = ""


class TieredEvidence(BaseModel):
    primaryEvidence: list[dict[str, Any]] = Field(default_factory=list)
    secondaryEvidence: list[dict[str, Any]] = Field(default_factory=list)
    caseReference: list[dict[str, Any]] = Field(default_factory=list)
    modernSupport: list[dict[str, Any]] = Field(default_factory=list)
    excludedOrLowTrust: list[dict[str, Any]] = Field(default_factory=list)


class LiuyaoJudgementReport(BaseModel):
    steps: list[JudgementStep] = Field(default_factory=list)
    topic: dict[str, Any] = Field(default_factory=dict)
    yongShen: dict[str, Any] = Field(default_factory=dict)
    judges: list[LiuyaoJudgeVerdict] = Field(default_factory=list)
    arbitration: ArbitrationResult = Field(default_factory=ArbitrationResult)
    evidenceChain: list[EvidenceChainItem] = Field(default_factory=list)
    tieredEvidence: TieredEvidence = Field(default_factory=TieredEvidence)
    tieredEvidenceSummary: dict[str, Any] = Field(default_factory=dict)
    enrichedChart: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
