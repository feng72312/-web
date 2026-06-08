from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

SchoolId = Literal["guolao_v1"]
DayNightRule = Literal["auto", "day", "night"]


@dataclass(frozen=True)
class XingmingRules:
    school: SchoolId = "guolao_v1"
    zi_hour_rule: Literal["combined", "split"] = "combined"
    day_night_rule: DayNightRule = "auto"

    def as_meta(self) -> dict[str, str]:
        return {
            "school": self.school,
            "ziHourRule": self.zi_hour_rule,
            "dayNightRule": self.day_night_rule,
        }


def rules_from_payload(
    payload: dict[str, Any] | None,
    *,
    default_zi: str = "combined",
) -> XingmingRules:
    data = payload or {}
    school = data.get("school", "guolao_v1")
    if school not in ("guolao_v1",):
        raise ValueError(f"unsupported school: {school}")
    zi = data.get("ziHourRule", default_zi)
    if zi not in ("combined", "split"):
        raise ValueError(f"unsupported ziHourRule: {zi}")
    dn = data.get("dayNightRule", "auto")
    if dn not in ("auto", "day", "night"):
        raise ValueError(f"unsupported dayNightRule: {dn}")
    return XingmingRules(school=school, zi_hour_rule=zi, day_night_rule=dn)
