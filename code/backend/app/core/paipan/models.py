from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Pillar:
    gan: str
    zhi: str
    gan_wuxing: str
    zhi_wuxing: str
    nayin: str
    hide_gan: list[str] = field(default_factory=list)
    shishen_gan: str = ""
    shishen_zhi: list[str] = field(default_factory=list)

    @property
    def ganzhi(self) -> str:
        return f"{self.gan}{self.zhi}"


@dataclass
class DayunItem:
    index: int
    ganzhi: str
    start_age: int
    end_age: int
    start_year: int


@dataclass
class PaipanInput:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    gender: int
    second: int = 0
    name: str = ""
    calendar_type: str = "solar"
    is_leap_month: bool = False


@dataclass
class PaipanResult:
    input: PaipanInput
    solar: str
    lunar: str
    pillars: dict[str, Pillar]
    day_master: str
    day_master_wuxing: str
    wuxing_count: dict[str, int]
    dayun: list[DayunItem]
    dayun_start: dict[str, int]
    dayun_forward: bool
    meta: dict[str, Any] = field(default_factory=dict)
    pillar_detail: dict[str, Any] = field(default_factory=dict)
    luck_timeline: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": {
                "name": self.input.name,
                "calendarType": self.input.calendar_type,
                "isLeapMonth": self.input.is_leap_month,
                "year": self.input.year,
                "month": self.input.month,
                "day": self.input.day,
                "hour": self.input.hour,
                "minute": self.input.minute,
                "second": self.input.second,
                "gender": self.input.gender,
            },
            "solar": self.solar,
            "lunar": self.lunar,
            "pillars": {
                key: {
                    "gan": p.gan,
                    "zhi": p.zhi,
                    "ganzhi": p.ganzhi,
                    "ganWuxing": p.gan_wuxing,
                    "zhiWuxing": p.zhi_wuxing,
                    "nayin": p.nayin,
                    "hideGan": p.hide_gan,
                    "shishenGan": p.shishen_gan,
                    "shishenZhi": p.shishen_zhi,
                }
                for key, p in self.pillars.items()
            },
            "dayMaster": self.day_master,
            "dayMasterWuxing": self.day_master_wuxing,
            "wuxingCount": self.wuxing_count,
            "dayun": [
                {
                    "index": d.index,
                    "ganzhi": d.ganzhi,
                    "startAge": d.start_age,
                    "endAge": d.end_age,
                    "startYear": d.start_year,
                }
                for d in self.dayun
            ],
            "dayunStart": self.dayun_start,
            "dayunForward": self.dayun_forward,
            "meta": self.meta,
            "pillarDetail": self.pillar_detail,
            "luckTimeline": self.luck_timeline,
        }
