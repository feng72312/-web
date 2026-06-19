from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.schemas.paipan import PaipanRequest


class JudgementRequest(BaseModel):
    """Reuse paipan birth fields via router helper."""

    includeRag: bool = True


class PaipanJudgementRequest(PaipanRequest):
    question: str = Field(default="", max_length=200)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()


class JudgementResponse(BaseModel):
    chart: dict[str, Any]
    sections: list[dict[str, Any]] = Field(default_factory=list)
    judgement: dict[str, Any]
    tieredEvidenceSummary: dict[str, Any] = Field(default_factory=dict)
