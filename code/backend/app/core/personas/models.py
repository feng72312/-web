from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PersonaLicense(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80)
    attribution: str = Field(min_length=1, max_length=240)
    source_url: str = Field(min_length=1, max_length=500)


class PersonaUpstream(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    url: str = Field(min_length=1, max_length=500)
    owner: str = Field(default="", max_length=120)
    commit: str = Field(default="", max_length=64)


class PersonaManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=64)
    name: str = Field(min_length=1, max_length=80)
    formal_name: str = Field(min_length=1, max_length=120)
    era: str = Field(min_length=1, max_length=80)
    lifespan: str = Field(min_length=1, max_length=80)
    status: Literal["historical-deceased", "living", "unknown"]
    category_id: str = Field(default="chinese-philosophers", max_length=80)
    category_label: str = Field(default="中国哲学家", max_length=80)
    life_status: Literal["historical", "living", "unknown"] = "historical"
    interaction_mode: Literal["historical_simulation", "public_framework"] = "historical_simulation"
    availability: Literal["ready", "review_required", "unavailable"] = "ready"
    availability_reason: str = Field(default="已通过人物包审核", max_length=400)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$", max_length=24)
    summary: str = Field(min_length=20, max_length=600)
    disclosure: str = Field(min_length=20, max_length=400)
    seal_character: str = Field(min_length=1, max_length=4)
    themes: list[str] = Field(min_length=1, max_length=12)
    suitable_for: list[str] = Field(min_length=1, max_length=12)
    not_suitable_for: list[str] = Field(min_length=1, max_length=12)
    upstream: PersonaUpstream
    license: PersonaLicense

    @model_validator(mode="after")
    def validate_lifecycle_mode(self) -> "PersonaManifest":
        if self.status in {"living", "unknown"} and self.interaction_mode != "public_framework":
            raise ValueError("living or unknown personas must use public_framework")
        return self


class PersonaSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    title: str = Field(min_length=1, max_length=180)
    kind: Literal["primary", "research", "upstream", "critical"]
    note: str = Field(min_length=1, max_length=500)
    citation: str | None = Field(default=None, max_length=240)
    url: str | None = Field(default=None, max_length=500)


class PersonaStarter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=80)
    prompt: str = Field(min_length=2, max_length=500)
    theme: str = Field(min_length=1, max_length=80)


class PersonaPack(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    manifest: PersonaManifest
    prompt: str
    sources: list[PersonaSource]
    starters: list[PersonaStarter]
    license_text: str

    def public_summary(self) -> dict[str, object]:
        data = self.manifest.model_dump(by_alias=True)
        data.pop("not_suitable_for", None)
        return data

    def public_detail(self) -> dict[str, object]:
        data = self.manifest.model_dump(by_alias=True)
        data["sources"] = [item.model_dump() for item in self.sources]
        data["starters"] = [item.model_dump() for item in self.starters]
        return data
