from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from app.core.xingming.rules import XingmingRules


@dataclass
class XingmingInput:
    name: str = ""
    calendar_type: Literal["solar", "lunar"] = "solar"
    year: int = 1990
    month: int = 1
    day: int = 1
    is_leap_month: bool = False
    hour: int = 12
    minute: int = 0
    second: int = 0
    gender: int = 1
    use_true_solar_time: bool = True
    longitude: float = 120.0
    latitude: float = 35.0
    target_year: int | None = None
    question: str = ""
    rules: XingmingRules = field(default_factory=XingmingRules)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "calendarType": self.calendar_type,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "isLeapMonth": self.is_leap_month,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
            "gender": self.gender,
            "useTrueSolarTime": self.use_true_solar_time,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "targetYear": self.target_year,
            "question": self.question,
            "rules": self.rules.as_meta(),
        }


@dataclass
class XingmingChartResult:
    chart: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return self.chart
