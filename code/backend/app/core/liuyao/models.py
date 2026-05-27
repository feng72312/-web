from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


LIUQIN_NAMES = ("父母", "兄弟", "子孙", "妻财", "官鬼")
CastMethod = Literal["coin", "number", "time"]


@dataclass
class LiuyaoInput:
    question: str
    method: CastMethod
    coin_lines: list[int] | None = None
    numbers: list[int] | None = None
    year: int = 2000
    month: int = 1
    day: int = 1
    hour: int = 0
    minute: int = 0
    second: int = 0
    calendar_type: str = "solar"
    is_leap_month: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "method": self.method,
            "coinLines": self.coin_lines,
            "numbers": self.numbers,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
            "calendarType": self.calendar_type,
            "isLeapMonth": self.is_leap_month,
        }


@dataclass
class YongShenResult:
    yong_shen: str
    position: int
    reason: str
    source: str = "ai"

    def to_dict(self) -> dict[str, Any]:
        return {
            "yongShen": self.yong_shen,
            "position": self.position,
            "reason": self.reason,
            "source": self.source,
        }


@dataclass
class LiuyaoLine:
    position: int
    value: int
    is_moving: bool
    is_yang: bool
    branch: str
    stem: str
    liuqin: str
    liushen: str
    is_shi: bool = False
    is_ying: bool = False
    fu_shen: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": self.position,
            "value": self.value,
            "isMoving": self.is_moving,
            "isYang": self.is_yang,
            "branch": self.branch,
            "stem": self.stem,
            "liuqin": self.liuqin,
            "liushen": self.liushen,
            "isShi": self.is_shi,
            "isYing": self.is_ying,
            "fuShen": self.fu_shen,
        }


@dataclass
class GuaInfo:
    name: str
    upper: str
    lower: str
    palace: str
    palace_element: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "lower": self.lower,
            "upper": self.upper,
            "palace": self.palace,
            "palaceElement": self.palace_element,
        }


@dataclass
class LiuyaoChart:
    input: LiuyaoInput
    ben_gua: GuaInfo
    bian_gua: GuaInfo | None
    lines: list[LiuyaoLine]
    moving_lines: list[int]
    shi_ying: dict[str, int]
    month_jian: str
    day_chen: str
    day_gan: str
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": self.input.to_dict(),
            "benGua": self.ben_gua.to_dict(),
            "bianGua": self.bian_gua.to_dict() if self.bian_gua else None,
            "lines": [line.to_dict() for line in self.lines],
            "movingLines": self.moving_lines,
            "shiYing": self.shi_ying,
            "monthJian": self.month_jian,
            "dayChen": self.day_chen,
            "dayGan": self.day_gan,
            "meta": self.meta,
        }

    def liuqin_positions(self) -> dict[str, list[int]]:
        grouped: dict[str, list[int]] = {name: [] for name in LIUQIN_NAMES}
        for line in self.lines:
            grouped.setdefault(line.liuqin, []).append(line.position)
        return grouped
