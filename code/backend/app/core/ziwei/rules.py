from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

LeapMonthRule = Literal["next_month", "midmonth_split"]
ZiHourRule = Literal["combined", "split"]
MutagenTable = Literal["nan_pai", "geng_beipai", "wu_pai", "ren_pai"]


@dataclass(frozen=True)
class ZiweiRules:
    leap_month_rule: LeapMonthRule = "next_month"
    zi_hour_rule: ZiHourRule = "combined"
    mutagen_table: MutagenTable = "nan_pai"

    def as_meta(self) -> dict[str, str]:
        return {
            "leapMonthRule": self.leap_month_rule,
            "ziHourRule": self.zi_hour_rule,
            "mutagenTable": self.mutagen_table,
        }

    def warnings(self) -> list[str]:
        if self.mutagen_table != "nan_pai":
            return [f"mutagenTable {self.mutagen_table} not implemented; using nan_pai"]
        return []

    def iztro_fix_leap(self) -> bool:
        return self.leap_month_rule == "next_month"


def rules_from_payload(
    payload: dict[str, Any] | None,
    *,
    default_leap: str = "next_month",
    default_zi: str = "combined",
    default_mutagen: str = "nan_pai",
) -> ZiweiRules:
    data = payload or {}
    leap = str(data.get("leapMonthRule") or default_leap)
    zi = str(data.get("ziHourRule") or default_zi)
    mutagen = str(data.get("mutagenTable") or default_mutagen)
    if leap not in ("next_month", "midmonth_split"):
        leap = "next_month"
    if zi not in ("combined", "split"):
        zi = "combined"
    if mutagen not in ("nan_pai", "geng_beipai", "wu_pai", "ren_pai"):
        mutagen = "nan_pai"
    return ZiweiRules(
        leap_month_rule=leap,  # type: ignore[arg-type]
        zi_hour_rule=zi,  # type: ignore[arg-type]
        mutagen_table=mutagen,  # type: ignore[arg-type]
    )
