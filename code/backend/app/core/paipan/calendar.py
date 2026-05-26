from __future__ import annotations

from lunar_python import Lunar, Solar

from app.core.paipan.models import PaipanInput


def resolve_solar_lunar(data: PaipanInput) -> tuple[Solar, Lunar, str]:
    if data.calendar_type == "lunar":
        lunar_month = -data.month if data.is_leap_month else data.month
        lunar = Lunar.fromYmdHms(
            data.year,
            lunar_month,
            data.day,
            data.hour,
            data.minute,
            data.second,
        )
        solar = lunar.getSolar()
        label = lunar.toString()
    else:
        solar = Solar.fromYmdHms(
            data.year,
            data.month,
            data.day,
            data.hour,
            data.minute,
            data.second,
        )
        lunar = solar.getLunar()
        label = solar.toYmdHms()
    return solar, lunar, label
