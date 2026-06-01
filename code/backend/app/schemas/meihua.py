from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin


class MeihuaDivineRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    method: Literal["number", "time"]
    numbers: list[int] | None = None
    year: int = Field(default=2000, ge=1900, le=2100)
    month: int = Field(default=1, ge=1, le=12)
    day: int = Field(default=1, ge=1, le=31)
    hour: int = Field(default=0, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)
    calendarType: str = Field(default="solar")
    isLeapMonth: bool = False
    movingPositionOverride: int | None = Field(default=None, ge=1, le=6)

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


class MeihuaTiYongRequest(BaseModel):
    chart: dict[str, Any]
    movingPosition: int = Field(ge=1, le=6)


class MeihuaRagSearchRequest(BaseModel):
    chart: dict[str, Any]
    question: str | None = None


class MeihuaInterpretRequest(BaseModel, InterpretStyleMixin):
    chart: dict[str, Any]
    question: str | None = None
    excerpts: list[dict[str, str]] | None = None
    model: str | None = None


class MeihuaChatInitRequest(BaseModel):
    chart: dict[str, Any]
    excerpts: list[dict[str, str]] | None = None
    knowledgeHits: list[dict[str, Any]] | None = None


class MeihuaDivineResponse(BaseModel):
    chart: dict[str, Any]


class MeihuaTiYongResponse(BaseModel):
    chart: dict[str, Any]


class MeihuaRagSearchResponse(BaseModel):
    query: str
    excerpts: list[dict[str, str]]


class MeihuaInterpretResponse(BaseModel):
    chart: dict[str, Any]
    interpretation: dict[str, Any]
