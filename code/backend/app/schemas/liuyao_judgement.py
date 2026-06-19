from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LiuyaoJudgementRequest(BaseModel):
    chart: dict[str, Any]
    question: str = ""
    yongShen: dict[str, Any] | None = None
    yongShenOverride: bool = False
    useRag: bool = True


class LiuyaoJudgementResponse(BaseModel):
    judgement: dict[str, Any]
    confidence: float = 0.5
    confidenceBand: str = "medium"
    conflicts: list[str] = Field(default_factory=list)
