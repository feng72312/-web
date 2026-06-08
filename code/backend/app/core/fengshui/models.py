from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

FengshuiMethod = Literal["bazhai", "xuankong"]
FengshuiScene = Literal["residence", "shop", "office"]


@dataclass
class FengshuiInput:
    question: str
    method: FengshuiMethod = "bazhai"
    scene: FengshuiScene = "residence"
    birth_year: int = 1990
    gender: int = 1
    sitting_mountain: str = "zi"
    build_year: int | None = None
    flow_year: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "question": self.question,
            "method": self.method,
            "scene": self.scene,
            "birthYear": self.birth_year,
            "gender": self.gender,
            "sittingMountain": self.sitting_mountain,
        }
        if self.build_year is not None:
            payload["buildYear"] = self.build_year
        if self.flow_year is not None:
            payload["flowYear"] = self.flow_year
        return payload


@dataclass
class FengshuiChart:
    input: FengshuiInput
    ming_gua: dict[str, Any] | None = None
    zhai_gua: dict[str, Any] | None = None
    compatible: bool | None = None
    directions: list[dict[str, Any]] = field(default_factory=list)
    palaces: list[dict[str, Any]] = field(default_factory=list)
    advice: list[str] = field(default_factory=list)
    xuankong: dict[str, Any] | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "input": self.input.to_dict(),
            "meta": self.meta,
        }
        if self.ming_gua is not None:
            payload["mingGua"] = self.ming_gua
        if self.zhai_gua is not None:
            payload["zhaiGua"] = self.zhai_gua
        if self.compatible is not None:
            payload["compatible"] = self.compatible
        if self.directions:
            payload["directions"] = self.directions
        if self.palaces:
            payload["palaces"] = self.palaces
        if self.advice:
            payload["advice"] = self.advice
        if self.xuankong is not None:
            payload["xuankong"] = self.xuankong
        return payload
