from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ZhugeDivineRequest(BaseModel):
    chars: str = Field(..., min_length=3, max_length=12)
    strokes: list[int] | None = None
    question: str = ""


class ZhugeDivineResponse(BaseModel):
    chars: str
    rawStrokes: list[int]
    reducedStrokes: list[int]
    qianNo: int
    qianText: str
    steps: list[str]
    missingText: bool = False


class JiemengSearchRequest(BaseModel):
    dream: str = Field(..., min_length=2, max_length=500)
    limit: int = Field(default=8, ge=1, le=20)


class JiemengMatch(BaseModel):
    section: str
    text: str
    score: str


class JiemengSearchResponse(BaseModel):
    dream: str
    matches: list[JiemengMatch]


class CewenRagSearchRequest(BaseModel):
    chars: str = Field(..., min_length=1, max_length=20)
    question: str = ""


class UtilsRagSearchResponse(BaseModel):
    query: str
    excerpts: list[dict[str, str]]


class UtilsInterpretRequest(BaseModel):
    tool: str
    payload: dict[str, Any]
    question: str = ""
    excerpts: list[dict[str, str]] | None = None
    model: str | None = None
    style: str | None = None


class UtilsInterpretation(BaseModel):
    tool: str
    payload: dict[str, Any]
    excerpts: list[dict[str, str]]
    summary: str | None = None
    agentId: str | None = None


class UtilsInterpretResponse(BaseModel):
    interpretation: UtilsInterpretation


class NamingBirthInput(BaseModel):
    calendarType: str = Field(default="solar")
    year: int = Field(ge=1900, le=2100)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour: int = Field(default=12, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)
    gender: int = Field(default=1, description="1=male, 0=female")
    isLeapMonth: bool = False


class NamingAnalyzeRequest(BaseModel):
    surname: str = Field(..., min_length=1, max_length=8)
    givenName: str = Field(default="", max_length=8)
    strokeOverrides: dict[str, int] | None = None
    birth: NamingBirthInput | None = None


class NamingAnalyzeResponse(BaseModel):
    analysis: dict[str, Any]


class NamingLookupRequest(BaseModel):
    chars: str = Field(..., min_length=1, max_length=20)


class NamingLookupResponse(BaseModel):
    chars: str
    entries: list[dict[str, Any]]


class NamingRagSearchRequest(BaseModel):
    surname: str = Field(..., min_length=1, max_length=8)
    givenName: str = Field(default="", max_length=8)
    question: str = ""
    birth: NamingBirthInput | None = None
    strokeOverrides: dict[str, int] | None = None
