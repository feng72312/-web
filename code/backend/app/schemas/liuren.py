from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin


class BirthProfileSummary(BaseModel):
    """Optional natal chart context for AI only (not used in liuren cast)."""

    year: str = ""
    month: str = ""
    day: str = ""
    hour: str = ""
    gender: str = ""
    summary: str = ""


class LiurenChartRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    castMethod: Literal["liuren", "jinkou", "both"] = "liuren"
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
    jinkouDifen: str = Field(default="", max_length=2)
    guiRenMode: int = Field(default=0, ge=0, le=1)

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


class LiurenRagSearchRequest(BaseModel):
    chart: dict[str, Any]
    question: str | None = None


class LiurenInterpretRequest(BaseModel, InterpretStyleMixin):
    chart: dict[str, Any]
    question: str | None = None
    excerpts: list[dict[str, str]] | None = None
    model: str | None = None


class LiurenChatInitRequest(BaseModel):
    chart: dict[str, Any]
    excerpts: list[dict[str, str]] | None = None
    knowledgeHits: list[dict[str, Any]] | None = None


class LiurenChartResponse(BaseModel):
    chart: dict[str, Any]


class LiurenRagSearchResponse(BaseModel):
    query: str
    excerpts: list[dict[str, str]]


class LiurenInterpretResponse(BaseModel):
    chart: dict[str, Any]
    interpretation: dict[str, Any]


class LiurenMethodInfo(BaseModel):
    id: str
    label: str
    implemented: bool


class LiurenMethodsResponse(BaseModel):
    methods: list[LiurenMethodInfo]
