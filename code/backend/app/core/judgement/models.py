from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

ConfidenceBand = Literal["strong", "medium", "weak"]
JudgeRole = Literal[
    "month",
    "tiaohou",
    "geju",
    "qishi",
    "shishen",
    "suiyun",
    "interactions",
    "base",
    "comprehensive",
    "case",
]
StepStatus = Literal["pending", "ok", "partial", "skipped"]
ConclusionKind = Literal[
    "classic_direct",
    "rule_derived",
    "experience_reference",
    "insufficient_evidence",
]


class JudgementStep(BaseModel):
    id: str
    label: str
    status: StepStatus = "pending"
    summary: str = ""


class EvidenceRequest(BaseModel):
    ruleId: str = ""
    topic: str = ""
    sourceScope: List[str] = Field(default_factory=list)
    libraryRoles: List[str] = Field(default_factory=list)
    classicWhitelist: List[str] = Field(default_factory=list)
    authorityTiers: List[str] = Field(default_factory=list)
    evidenceRoles: List[str] = Field(default_factory=list)
    query: str = ""
    judgeOnly: bool = False


class JudgeVerdict(BaseModel):
    role: JudgeRole
    classic: str = ""
    summary: str = ""
    stance: str = "neutral"
    ruleIds: List[str] = Field(default_factory=list)
    confidenceBand: ConfidenceBand = "medium"
    conclusionKind: ConclusionKind = "rule_derived"
    boundary: str = ""


class EvidenceChainItem(BaseModel):
    conclusion: str
    ruleId: str = ""
    primaryClassic: str = ""
    quote: str = ""
    secondary: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    boundary: str = ""
    confidence: ConfidenceBand = "medium"
    conclusionKind: ConclusionKind = "rule_derived"


class ArbitrationResult(BaseModel):
    judgeOpinions: List[JudgeVerdict] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    finalBoundaries: List[str] = Field(default_factory=list)
    confidenceScore: float = 0.5
    confidenceBand: ConfidenceBand = "medium"
    evidenceRequests: List[EvidenceRequest] = Field(default_factory=list)


class TieredEvidence(BaseModel):
    primaryEvidence: List[Dict[str, Any]] = Field(default_factory=list)
    secondaryEvidence: List[Dict[str, Any]] = Field(default_factory=list)
    caseReference: List[Dict[str, Any]] = Field(default_factory=list)
    excludedOrLowTrust: List[Dict[str, Any]] = Field(default_factory=list)


class BaziJudgementReport(BaseModel):
    steps: List[JudgementStep] = Field(default_factory=list)
    arbitration: ArbitrationResult = Field(default_factory=ArbitrationResult)
    evidenceChain: List[EvidenceChainItem] = Field(default_factory=list)
    tieredEvidence: TieredEvidence = Field(default_factory=TieredEvidence)
    tieredEvidenceSummary: Dict[str, Any] = Field(default_factory=dict)
    lookupKeys: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
