from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin
from app.schemas.rag_excerpt import OptionalRagExcerptList, RagExcerptList


class BirthProfileSummary(BaseModel):
    """Optional natal chart for AI context only; not used in qimen cast."""

    year: str = ""
    month: str = ""
    day: str = ""
    hour: str = ""
    gender: str = ""
    summary: str = ""


class QimenChartRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    category: Literal["shizhan", "xingzhan"] = "shizhan"
    year: int = Field(default=2000, ge=1900, le=2100)
    month: int = Field(default=1, ge=1, le=12)
    day: int = Field(default=1, ge=1, le=31)
    hour: int = Field(default=0, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)
    calendarType: str = Field(default="solar")
    isLeapMonth: bool = False
    useTrueSolarTime: bool = False
    longitude: float = Field(default=120.0, ge=70.0, le=140.0)
    direction: str = Field(default="", max_length=32)
    method: Literal["chaibu", "zhirun", "maoshan"] = "chaibu"
    juOverride: int | None = Field(default=None, ge=1, le=9)
    birthProfile: BirthProfileSummary | None = None

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


class QimenRagSearchRequest(BaseModel):
    chart: dict[str, Any]
    question: str | None = None


class QimenInterpretRequest(BaseModel, InterpretStyleMixin):
    chart: dict[str, Any]
    question: str | None = None
    excerpts: OptionalRagExcerptList = None
    model: str | None = None
    birthProfile: BirthProfileSummary | None = None


class QimenChatInitRequest(BaseModel):
    chart: dict[str, Any]
    excerpts: OptionalRagExcerptList = None
    knowledgeHits: list[dict[str, Any]] | None = None
    birthProfile: BirthProfileSummary | None = None


class QimenChartResponse(BaseModel):
    chart: dict[str, Any]


class QimenRagSearchResponse(BaseModel):
    query: str
    excerpts: RagExcerptList


class QimenInterpretResponse(BaseModel):
    chart: dict[str, Any]
    interpretation: dict[str, Any]


class QimenMethodInfo(BaseModel):
    id: str
    label: str
    implemented: bool


class QimenMethodsResponse(BaseModel):
    methods: list[QimenMethodInfo]
