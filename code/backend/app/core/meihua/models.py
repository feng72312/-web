from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

CastMethod = Literal["number", "time"]


@dataclass
class MeihuaInput:
    question: str
    method: CastMethod
    numbers: list[int] | None = None
    year: int = 2000
    month: int = 1
    day: int = 1
    hour: int = 0
    minute: int = 0
    second: int = 0
    calendar_type: str = "solar"
    is_leap_month: bool = False
    moving_position_override: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "method": self.method,
            "numbers": self.numbers,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
            "calendarType": self.calendar_type,
            "isLeapMonth": self.is_leap_month,
            "movingPositionOverride": self.moving_position_override,
        }


@dataclass
class TrigramInfo:
    name: str
    element: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "element": self.element}


@dataclass
class BenGuaInfo:
    name: str
    lower: str
    upper: str
    lower_element: str
    upper_element: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "lower": self.lower,
            "upper": self.upper,
            "lowerElement": self.lower_element,
            "upperElement": self.upper_element,
        }


@dataclass
class MeihuaLine:
    position: int
    value: int
    is_moving: bool
    is_yang: bool
    in_lower: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": self.position,
            "value": self.value,
            "isMoving": self.is_moving,
            "isYang": self.is_yang,
            "inLower": self.in_lower,
        }


@dataclass
class MeihuaChart:
    input: MeihuaInput
    ben_gua: BenGuaInfo
    bian_gua: BenGuaInfo | None
    lines: list[MeihuaLine]
    moving_lines: list[int]
    ti_gua: TrigramInfo
    yong_gua: TrigramInfo
    ti_yong_relation: str
    hu_gua: BenGuaInfo | None
    is_static: bool
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": self.input.to_dict(),
            "benGua": self.ben_gua.to_dict(),
            "bianGua": self.bian_gua.to_dict() if self.bian_gua else None,
            "lines": [line.to_dict() for line in self.lines],
            "movingLines": self.moving_lines,
            "tiGua": self.ti_gua.to_dict(),
            "yongGua": self.yong_gua.to_dict(),
            "tiYongRelation": self.ti_yong_relation,
            "huGua": self.hu_gua.to_dict() if self.hu_gua else None,
            "isStatic": self.is_static,
            "meta": self.meta,
        }
