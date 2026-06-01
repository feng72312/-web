from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

QimenMethod = Literal["chaibu", "zhirun", "maoshan"]
QimenCategory = Literal["shizhan", "xingzhan"]


@dataclass
class QimenInput:
    question: str
    category: QimenCategory = "shizhan"
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
    direction: str = ""
    method: QimenMethod = "chaibu"
    ju_override: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
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
            "direction": self.direction,
            "method": self.method,
            "juOverride": self.ju_override,
        }


@dataclass
class PalaceCell:
    index: int
    name: str
    earth: str = ""
    heaven: str = ""
    human: str = ""
    star: str = ""
    door: str = ""
    god: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "name": self.name,
            "earth": self.earth,
            "heaven": self.heaven,
            "human": self.human,
            "star": self.star,
            "door": self.door,
            "god": self.god,
        }


@dataclass
class JuInfo:
    dun_type: str
    ju_number: int
    yuan: str
    jieqi: str
    ju_name: str
    fu_tou: str = ""
    xun_shou: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "dunType": self.dun_type,
            "juNumber": self.ju_number,
            "yuan": self.yuan,
            "jieqi": self.jieqi,
            "juName": self.ju_name,
            "fuTou": self.fu_tou,
            "xunShou": self.xun_shou,
        }


@dataclass
class ZhiFuZhiShi:
    zhi_fu_star: str
    zhi_fu_gong: str
    zhi_fu_gan: str
    zhi_shi_door: str
    zhi_shi_gong: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "zhiFuStar": self.zhi_fu_star,
            "zhiFuGong": self.zhi_fu_gong,
            "zhiFuGan": self.zhi_fu_gan,
            "zhiShiDoor": self.zhi_shi_door,
            "zhiShiGong": self.zhi_shi_gong,
        }


@dataclass
class QimenChart:
    input: QimenInput
    ju: JuInfo
    zhi_fu_zhi_shi: ZhiFuZhiShi
    palaces: list[PalaceCell]
    four_pillars: dict[str, str]
    true_solar_time: str
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": self.input.to_dict(),
            "ju": self.ju.to_dict(),
            "zhiFuZhiShi": self.zhi_fu_zhi_shi.to_dict(),
            "palaces": [p.to_dict() for p in self.palaces],
            "fourPillars": self.four_pillars,
            "trueSolarTime": self.true_solar_time,
            "meta": self.meta,
        }
