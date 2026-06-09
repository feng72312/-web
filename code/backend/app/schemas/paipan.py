from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin


class PaipanRequest(BaseModel):
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


class PaipanResponse(BaseModel):
    chart: Dict
    sections: List[dict]
    modules: List[dict]


class InterpretRequest(PaipanRequest, InterpretStyleMixin):
    """Optional pre-fetched RAG excerpts from /rag/search."""

    excerpts: Optional[List[dict]] = None
    question: str = Field(default="", max_length=200)
    model: Optional[str] = None
    fusion: bool = True
    fusionMode: Literal["bazi_liuyao", "bazi_ziwei", "triple"] = "bazi_liuyao"

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()
