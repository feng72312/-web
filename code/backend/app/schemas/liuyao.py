from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin
from app.schemas.rag_excerpt import OptionalRagExcerptList, RagExcerptList


class LiuyaoDivineRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    method: Literal["coin", "number", "time"]
    coinLines: list[int] | None = None
    numbers: list[int] | None = None
    year: int = Field(default=2000, ge=1900, le=2100)
    month: int = Field(default=1, ge=1, le=12)
    day: int = Field(default=1, ge=1, le=31)
    hour: int = Field(default=0, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)
    calendarType: str = Field(default="solar")
    isLeapMonth: bool = False

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()

    @field_validator("calendarType")
    @classmethod
    def validate_calendar_type(cls, value: str) -> str:
        if value not in ("solar", "lunar"):
            raise ValueError("calendarType must be solar or lunar")
        return value


class LiuyaoChartPayload(BaseModel):
    chart: dict[str, Any]


class LiuyaoInferYongShenRequest(BaseModel):
    chart: dict[str, Any]
    question: str = Field(min_length=1, max_length=200)
    model: str | None = None


class LiuyaoYongShenOverrideRequest(BaseModel):
    chart: dict[str, Any]
    yongShen: str
    position: int | None = Field(default=None, ge=1, le=6)


class LiuyaoRagSearchRequest(BaseModel):
    chart: dict[str, Any]
    yongShen: dict[str, Any]
    question: str | None = None


class LiuyaoInterpretRequest(BaseModel, InterpretStyleMixin):
    chart: dict[str, Any]
    question: str | None = None
    yongShen: dict[str, Any] | None = None
    excerpts: OptionalRagExcerptList = None
    model: str | None = None


class LiuyaoChatInitRequest(BaseModel):
    chart: dict[str, Any]
    yongShen: dict[str, Any]
    excerpts: OptionalRagExcerptList = None


class LiuyaoDivineResponse(BaseModel):
    chart: dict[str, Any]


class YongShenResponse(BaseModel):
    yongShen: str
    position: int
    reason: str
    source: str
    confidence: float = 0.5
    topicId: str = ""
    ruleId: str = ""


class LiuyaoRagSearchResponse(BaseModel):
    query: str
    excerpts: RagExcerptList


class LiuyaoInterpretResponse(BaseModel):
    chart: dict[str, Any]
    interpretation: dict[str, Any]
