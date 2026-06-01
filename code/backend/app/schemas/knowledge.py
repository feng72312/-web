from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.paipan import PaipanRequest


class KnowledgeClaimOut(BaseModel):
    classic: str
    edition: str = ""
    chapter: str
    quote: str
    conclusion: str
    role: str
    aligns: bool | None = None
    sourceFile: str
    sourceCategory: str


class KnowledgeHitOut(BaseModel):
    id: str
    topic: str
    lookupKey: dict[str, str]
    summary: str
    claims: list[KnowledgeClaimOut]
    agreementLevel: str
    safeAutoAnswer: bool
    sourceTier: str
    domain: str


class KnowledgeLookupRequest(PaipanRequest):
    topics: list[str] | None = None


class KnowledgeLookupResponse(BaseModel):
    lookupKeys: dict[str, Any]
    hits: list[KnowledgeHitOut]
    missingTopics: list[str]
    autoAnswerSummary: str | None = None
    directAnswer: str | None = None


class KnowledgeStatusResponse(BaseModel):
    enabled: bool
    dataDir: str
    manifestVersion: str
    nodeCount: int
    entryCounts: dict[str, int]
    reviewedCounts: dict[str, int] = Field(default_factory=dict)
    filesIndexed01: int = 0
    crossCategoryCount: int = 0
    loadError: str | None = None
