from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin
from app.schemas.rag_excerpt import OptionalRagExcerptList, RagExcerptList


class ZiweiRulesPayload(BaseModel):
    leapMonthRule: Literal["next_month", "midmonth_split"] = "next_month"
    ziHourRule: Literal["combined", "split"] = "combined"
    mutagenTable: Literal["nan_pai", "geng_beipai", "wu_pai", "ren_pai"] = "nan_pai"
    chartSchool: Literal["sanhe", "feixing"] = "sanhe"


class ZiweiChartRequest(BaseModel):
    name: str = Field(default="", max_length=32)
    calendarType: str = Field(default="solar")
    year: int = Field(ge=1900, le=2100)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    isLeapMonth: bool = False
    hour: int = Field(default=12, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)
    gender: int = Field(description="1=male, 0=female")
    useTrueSolarTime: bool = True
    longitude: float = Field(default=120.0, ge=70.0, le=140.0)
    targetYear: int | None = Field(default=None, ge=1900, le=2100)
    detailLevel: Literal["simple", "pro"] = "simple"
    question: str = Field(default="", max_length=200)
    rules: ZiweiRulesPayload = Field(default_factory=ZiweiRulesPayload)

    @field_validator("calendarType")
    @classmethod
    def validate_calendar_type(cls, value: str) -> str:
        if value not in ("solar", "lunar"):
            raise ValueError("calendarType must be solar or lunar")
        return value

    @field_validator("name", "question")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class ZiweiRagSearchRequest(BaseModel):
    chart: dict[str, Any]
    question: str | None = None


class ZiweiInterpretRequest(BaseModel, InterpretStyleMixin):
    chart: dict[str, Any]
    question: str | None = None
    excerpts: OptionalRagExcerptList = None
    model: str | None = None


class ZiweiChatInitRequest(BaseModel):
    chart: dict[str, Any]
    excerpts: OptionalRagExcerptList = None
    knowledgeHits: list[dict[str, Any]] | None = None


class ZiweiChartResponse(BaseModel):
    chart: dict[str, Any]


class ZiweiRagSearchResponse(BaseModel):
    query: str
    excerpts: RagExcerptList


class ZiweiInterpretResponse(BaseModel):
    chart: dict[str, Any]
    interpretation: dict[str, Any]


class ZiweiRulesOption(BaseModel):
    id: str
    label: str


class ZiweiRulesResponse(BaseModel):
    defaults: ZiweiRulesPayload
    leapMonthRules: list[ZiweiRulesOption]
    ziHourRules: list[ZiweiRulesOption]
    mutagenTables: list[ZiweiRulesOption]
    chartSchools: list[ZiweiRulesOption]
