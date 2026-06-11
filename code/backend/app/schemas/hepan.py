from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin
from app.schemas.rag_excerpt import OptionalRagExcerptList, RagExcerptList
from app.schemas.ziwei import ZiweiRulesPayload

HepanSceneField = Literal["romance", "marriage", "partnership"]
HepanDisciplineField = Literal["auto", "bazi", "ziwei"]


class HepanPersonRequest(BaseModel):
    name: str = Field(default="", max_length=32)
    calendarType: str = Field(default="solar")
    year: int = Field(ge=1900, le=2100)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    isLeapMonth: bool = False
    hour: int = Field(ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)
    gender: int = Field(description="1=male, 0=female")

    @field_validator("calendarType")
    @classmethod
    def validate_calendar_type(cls, value: str) -> str:
        if value not in ("solar", "lunar"):
            raise ValueError("calendarType must be solar or lunar")
        return value

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class HepanChartRequest(BaseModel):
    personA: HepanPersonRequest
    personB: HepanPersonRequest
    scene: HepanSceneField = "marriage"
    discipline: HepanDisciplineField = "auto"
    question: str = Field(default="", max_length=200)
    useTrueSolarTime: bool = True
    longitude: float = Field(default=120.0, ge=70.0, le=140.0)
    targetYear: int | None = Field(default=None, ge=1900, le=2100)
    ziweiRules: ZiweiRulesPayload = Field(default_factory=ZiweiRulesPayload)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()


class HepanCrossNote(BaseModel):
    id: str
    level: Literal["fit", "caution", "neutral"]
    dimension: str
    title: str
    detail: str
    source: Literal["bazi", "ziwei"]


class HepanPersonChartsOut(BaseModel):
    name: str
    gender: int
    baziChart: dict[str, Any] | None = None
    ziweiChart: dict[str, Any] | None = None


class HepanChartResponse(BaseModel):
    scene: HepanSceneField
    discipline: Literal["bazi", "ziwei"]
    personA: HepanPersonChartsOut
    personB: HepanPersonChartsOut
    crossNotes: list[HepanCrossNote]
    summaryTags: list[str]
    question: str


class HepanRagSearchRequest(BaseModel):
    hepan: dict[str, Any]
    question: str | None = None


class HepanRagSearchResponse(BaseModel):
    query: str
    excerpts: RagExcerptList


class HepanInterpretRequest(BaseModel, InterpretStyleMixin):
    hepan: dict[str, Any]
    question: str | None = None
    excerpts: OptionalRagExcerptList = None
    model: str | None = None


class HepanInterpretResponse(BaseModel):
    hepan: dict[str, Any]
    interpretation: dict[str, Any]


class HepanChatInitRequest(BaseModel):
    hepan: dict[str, Any]
    excerpts: OptionalRagExcerptList = None
    knowledgeHits: list[dict[str, Any]] | None = None


class HepanSceneOption(BaseModel):
    id: HepanSceneField
    label: str
    defaultDiscipline: Literal["bazi", "ziwei"]
    defaultQuestion: str


class HepanScenesResponse(BaseModel):
    scenes: list[HepanSceneOption]
