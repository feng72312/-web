from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

CastMethod = Literal["liuren", "jinkou", "both"]
LiurenCategory = Literal["shizhan", "xingzhan"]


@dataclass
class LiurenInput:
    question: str
    cast_method: CastMethod = "liuren"
    category: LiurenCategory = "shizhan"
    year: int = 2000
    month: int = 1
    day: int = 1
    hour: int = 0
    minute: int = 0
    second: int = 0
    calendar_type: str = "solar"
    is_leap_month: bool = False
    use_true_solar_time: bool = False
    longitude: float = 120.0
    jinkou_difen: str = ""
    gui_ren_mode: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "castMethod": self.cast_method,
            "category": self.category,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
            "calendarType": self.calendar_type,
            "isLeapMonth": self.is_leap_month,
            "useTrueSolarTime": self.use_true_solar_time,
            "longitude": self.longitude,
            "jinkouDifen": self.jinkou_difen,
            "guiRenMode": self.gui_ren_mode,
        }


@dataclass
class LiurenChart:
    input: LiurenInput
    four_pillars: dict[str, str]
    jieqi: str
    lunar_month: str
    yue_jiang: str
    si_ke: dict[str, Any]
    san_chuan: dict[str, Any]
    tian_di_pan: dict[str, Any]
    ge_ju: dict[str, Any]
    shen_sha: dict[str, str]
    true_solar_time: str
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fourPillars": self.four_pillars,
            "jieqi": self.jieqi,
            "lunarMonth": self.lunar_month,
            "yueJiang": self.yue_jiang,
            "siKe": self.si_ke,
            "sanChuan": self.san_chuan,
            "tianDiPan": self.tian_di_pan,
            "geJu": self.ge_ju,
            "shenSha": self.shen_sha,
            "trueSolarTime": self.true_solar_time,
            "meta": self.meta,
        }


@dataclass
class JinkouChart:
    ren_yuan: str
    gui_shen: list[str]
    jiang_shen: list[str]
    difen: str
    four_pillars: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "renYuan": self.ren_yuan,
            "guiShen": self.gui_shen,
            "jiangShen": self.jiang_shen,
            "difen": self.difen,
            "fourPillars": self.four_pillars,
        }


@dataclass
class LiurenResult:
    input: LiurenInput
    liuren: LiurenChart | None = None
    jinkou: JinkouChart | None = None
    true_solar_time: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "input": self.input.to_dict(),
            "trueSolarTime": self.true_solar_time,
            "meta": self.meta,
        }
        if self.liuren:
            payload["liuren"] = self.liuren.to_dict()
        if self.jinkou:
            payload["jinkou"] = self.jinkou.to_dict()
        return payload
