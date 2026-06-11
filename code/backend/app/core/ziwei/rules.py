from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

LeapMonthRule = Literal["next_month", "midmonth_split"]
ZiHourRule = Literal["combined", "split"]
MutagenTable = Literal["nan_pai", "geng_beipai", "wu_pai", "ren_pai"]
ChartSchool = Literal["sanhe", "feixing"]


@dataclass(frozen=True)
class ZiweiRules:
    leap_month_rule: LeapMonthRule = "next_month"
    zi_hour_rule: ZiHourRule = "combined"
    mutagen_table: MutagenTable = "nan_pai"
    chart_school: ChartSchool = "sanhe"

    def as_meta(self) -> dict[str, str]:
        return {
            "leapMonthRule": self.leap_month_rule,
            "ziHourRule": self.zi_hour_rule,
            "mutagenTable": self.mutagen_table,
            "chartSchool": self.chart_school,
        }

    def warnings(self) -> list[str]:
        return []

    def iztro_fix_leap(self) -> bool:
        return self.leap_month_rule == "next_month"


def rules_from_payload(
    payload: dict[str, Any] | None,
    *,
    default_leap: str = "next_month",
    default_zi: str = "combined",
    default_mutagen: str = "nan_pai",
    default_school: str = "sanhe",
) -> ZiweiRules:
    data = payload or {}
    leap = str(data.get("leapMonthRule") or default_leap)
    zi = str(data.get("ziHourRule") or default_zi)
    mutagen = str(data.get("mutagenTable") or default_mutagen)
    school = str(data.get("chartSchool") or default_school)
    if leap not in ("next_month", "midmonth_split"):
        leap = "next_month"
    if zi not in ("combined", "split"):
        zi = "combined"
    if mutagen not in ("nan_pai", "geng_beipai", "wu_pai", "ren_pai"):
        mutagen = "nan_pai"
    if school not in ("sanhe", "feixing"):
        school = "sanhe"
    return ZiweiRules(
        leap_month_rule=leap,  # type: ignore[arg-type]
        zi_hour_rule=zi,  # type: ignore[arg-type]
        mutagen_table=mutagen,  # type: ignore[arg-type]
        chart_school=school,  # type: ignore[arg-type]
    )
