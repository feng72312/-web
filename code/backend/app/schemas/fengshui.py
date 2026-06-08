from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin


class BirthProfileSummary(BaseModel):
    year: str = ""
    month: str = ""
    day: str = ""
    hour: str = ""
    gender: str = ""
    summary: str = ""


class FengshuiChartRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    method: Literal["bazhai", "xuankong"] = "bazhai"
    scene: Literal["residence", "shop", "office"] = "residence"
    birthYear: int = Field(default=1990, ge=1900, le=2100)
    gender: int = Field(default=1, ge=0, le=1)
    sittingMountain: str = Field(default="zi", min_length=1, max_length=8)
    buildYear: int | None = Field(default=None, ge=1864, le=2100)
    flowYear: int | None = Field(default=None, ge=1864, le=2100)
    birthProfile: BirthProfileSummary | None = None

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()

    @field_validator("sittingMountain")
    @classmethod
    def normalize_mountain(cls, value: str) -> str:
        return value.strip().lower()


class FengshuiRagSearchRequest(BaseModel):
    chart: dict[str, Any]
    question: str | None = None


class FengshuiInterpretRequest(BaseModel, InterpretStyleMixin):
    chart: dict[str, Any]
    question: str | None = None
    excerpts: list[dict[str, str]] | None = None
    model: str | None = None
    birthProfile: BirthProfileSummary | None = None


class FengshuiChatInitRequest(BaseModel):
    chart: dict[str, Any]
    excerpts: list[dict[str, str]] | None = None
    knowledgeHits: list[dict[str, Any]] | None = None
    birthProfile: BirthProfileSummary | None = None


class FengshuiChartResponse(BaseModel):
    chart: dict[str, Any]


class FengshuiRagSearchResponse(BaseModel):
    query: str
    excerpts: list[dict[str, str]]


class FengshuiInterpretResponse(BaseModel):
    chart: dict[str, Any]
    interpretation: dict[str, Any]


class FengshuiMethodInfo(BaseModel):
    id: str
    label: str
    implemented: bool


class FengshuiMethodsResponse(BaseModel):
    methods: list[FengshuiMethodInfo]


class FengshuiMountainInfo(BaseModel):
    id: str
    name: str
    trigram: str
    facing: str
    label: str


class FengshuiMountainsResponse(BaseModel):
    mountains: list[FengshuiMountainInfo]
