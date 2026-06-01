from __future__ import annotations

from typing import Dict, List, Literal, Optional, Any

from pydantic import BaseModel, Field


AgreementLevel = Literal["unanimous", "majority", "disputed", "single_source"]
SourceTier = Literal["T1", "T2", "T3", "T4"]
ClaimRole = Literal["primary", "corroboration", "contradiction"]


class KnowledgeClaim(BaseModel):
    classic: str
    edition: str = ""
    chapter: str
    quote: str
    conclusion: str
    role: ClaimRole
    aligns: Optional[bool] = None
    sourceFile: str
    sourceCategory: str


class KnowledgeNode(BaseModel):
    id: str
    topic: str
    sourceTier: SourceTier
    sourceCategory: str
    sourceFile: str
    lookupKey: Dict[str, str]
    summary: str
    claims: List[KnowledgeClaim]
    agreementLevel: AgreementLevel
    safeAutoAnswer: bool
    domain: str = "bazi"
    reviewedAt: Optional[str] = None


class KnowledgeHit(BaseModel):
    id: str
    topic: str
    lookupKey: Dict[str, str]
    summary: str
    claims: List[KnowledgeClaim]
    agreementLevel: AgreementLevel
    safeAutoAnswer: bool
    sourceTier: SourceTier
    domain: str


class CompressedContext(BaseModel):
    lookupKeys: Dict[str, Any] = Field(default_factory=dict)
    hits: List[KnowledgeHit] = Field(default_factory=list)
    missingTopics: List[str] = Field(default_factory=list)
    autoAnswerSummary: Optional[str] = None
    directAnswer: Optional[str] = None
    tokenEstimate: int = 0


class KnowledgeLookupResult(BaseModel):
    lookupKeys: Dict[str, Any] = Field(default_factory=dict)
    hits: List[KnowledgeHit] = Field(default_factory=list)
    missingTopics: List[str] = Field(default_factory=list)
    autoAnswerSummary: Optional[str] = None
    directAnswer: Optional[str] = None
