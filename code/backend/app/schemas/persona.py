from __future__ import annotations

from pydantic import BaseModel, Field


class PersonaLicenseOut(BaseModel):
    name: str
    attribution: str
    sourceUrl: str


class PersonaUpstreamOut(BaseModel):
    name: str
    url: str
    owner: str = ""
    commit: str = ""


class PersonaSummaryOut(BaseModel):
    id: str
    name: str
    formalName: str
    era: str
    lifespan: str
    version: str
    summary: str
    disclosure: str
    sealCharacter: str
    themes: list[str]
    suitableFor: list[str]
    categoryId: str
    categoryLabel: str
    lifeStatus: str
    interactionMode: str
    availability: str
    availabilityReason: str
    upstream: PersonaUpstreamOut
    license: PersonaLicenseOut


class PersonaSourceOut(BaseModel):
    id: str
    title: str
    kind: str
    note: str
    citation: str | None = None
    url: str | None = None


class PersonaStarterOut(BaseModel):
    label: str
    prompt: str
    theme: str


class PersonaDetailOut(PersonaSummaryOut):
    notSuitableFor: list[str]
    sources: list[PersonaSourceOut]
    starters: list[PersonaStarterOut]


class PersonaListResponse(BaseModel):
    personas: list[PersonaSummaryOut]
    categories: list["PersonaCategoryOut"] = []
    total: int = 0
    offset: int = 0
    limit: int = 24
    sourceCommit: str = ""


class PersonaCategoryOut(BaseModel):
    id: str
    label: str
    order: int
    count: int
    readyCount: int


class PersonaChatInitRequest(BaseModel):
    personaId: str = Field(min_length=1, max_length=64)
    title: str | None = Field(default=None, max_length=160)
    initialPrompt: str | None = Field(default=None, max_length=500)


class PersonaChatInitResponse(BaseModel):
    agentId: str
    personaId: str
    title: str
    disclosure: str
    interactionMode: str
