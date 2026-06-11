from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin
from app.schemas.rag_excerpt import OptionalRagExcerptList, RagExcerptList


class XingmingRulesPayload(BaseModel):
    school: Literal["guolao_v1"] = "guolao_v1"
    ziHourRule: Literal["combined", "split"] = "combined"
    dayNightRule: Literal["auto", "day", "night"] = "auto"


class XingmingChartRequest(BaseModel):
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
    latitude: float = Field(default=35.0, ge=15.0, le=55.0)
    targetYear: int | None = Field(default=None, ge=1900, le=2100)
    question: str = Field(default="", max_length=200)
    rules: XingmingRulesPayload = Field(default_factory=XingmingRulesPayload)

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


class XingmingRagSearchRequest(BaseModel):
    chart: dict[str, Any]
    question: str | None = None


class XingmingCasesSearchRequest(BaseModel):
    chart: dict[str, Any]
    question: str | None = None
    tier: str | None = "gold"
    topK: int = Field(default=5, ge=1, le=20)


class XingmingCrossCharts(BaseModel):
    baziChart: dict[str, Any] | None = None
    ziweiChart: dict[str, Any] | None = None


class XingmingInterpretRequest(BaseModel, InterpretStyleMixin):
    chart: dict[str, Any]
    question: str | None = None
    excerpts: OptionalRagExcerptList = None
    cases: list[dict[str, Any]] | None = None
    crossCharts: XingmingCrossCharts | None = None
    model: str | None = None


class XingmingChatInitRequest(BaseModel):
    chart: dict[str, Any]
    excerpts: OptionalRagExcerptList = None
    knowledgeHits: list[dict[str, Any]] | None = None
    cases: list[dict[str, Any]] | None = None
    crossCharts: XingmingCrossCharts | None = None


class XingmingChartResponse(BaseModel):
    chart: dict[str, Any]


class XingmingRagSearchResponse(BaseModel):
    query: str
    excerpts: RagExcerptList


class XingmingCasesSearchResponse(BaseModel):
    cases: list[dict[str, Any]]


class XingmingInterpretResponse(BaseModel):
    chart: dict[str, Any]
    interpretation: dict[str, Any]


class XingmingRulesOption(BaseModel):
    id: str
    label: str


class XingmingRulesResponse(BaseModel):
    defaults: XingmingRulesPayload
    schools: list[XingmingRulesOption]
    ziHourRules: list[XingmingRulesOption]
    dayNightRules: list[XingmingRulesOption]
