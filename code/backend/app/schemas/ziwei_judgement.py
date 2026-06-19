from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ZiweiJudgementRequest(BaseModel):
    chart: dict[str, Any]
    question: str = ""
    targetYear: int | None = Field(default=None, ge=1900, le=2100)
    school: str | None = None
    useRag: bool = True


class ZiweiJudgementResponse(BaseModel):
    judgement: dict[str, Any]
    confidence: float = 0.5
    confidenceBand: str = "medium"
    conflicts: list[str] = Field(default_factory=list)
