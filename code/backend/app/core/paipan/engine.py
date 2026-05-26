from __future__ import annotations

from app.core.paipan.calendar import resolve_solar_lunar
from app.core.paipan.detail_builder import build_pillar_detail, pillars_to_dict
from app.core.paipan.luck_builder import build_luck_timeline
from app.core.paipan.models import DayunItem, PaipanInput, PaipanResult, Pillar
from app.core.paipan.rules import PaipanRules

PILLAR_KEYS = ("year", "month", "day", "hour")
WUXING_KEYS = ("木", "火", "土", "金", "水")


class PaipanEngine:
    """Core chart calculator. Keep deterministic logic here, not in RAG."""

    def __init__(self, rules: PaipanRules | None = None) -> None:
        self.rules = rules or PaipanRules()

    def calculate(self, data: PaipanInput) -> PaipanResult:
        solar, lunar, input_label = resolve_solar_lunar(data)
        ec = lunar.getEightChar()
        ec.setSect(self.rules.sect)

        pillars = self._build_pillars(ec)
        wuxing_count = self._count_wuxing(pillars)
        solar_parts = solar.toYmdHms().split(" ")
        birth_year = int(solar_parts[0].split("-")[0])
        dayun, dayun_start, dayun_forward = self._build_dayun(ec, data.gender, birth_year)
        pillars_dict = pillars_to_dict(pillars)
        pillar_detail = build_pillar_detail(ec, pillars, data.gender)
        luck_timeline = build_luck_timeline(ec, data.gender, birth_year, pillars_dict)

        calendar_label = "农历" if data.calendar_type == "lunar" else "公历"
        leap_label = "(闰月)" if data.is_leap_month else ""

        return PaipanResult(
            input=data,
            solar=solar.toYmdHms(),
            lunar=lunar.toString(),
            pillars=pillars,
            day_master=pillars["day"].gan,
            day_master_wuxing=pillars["day"].gan_wuxing,
            wuxing_count=wuxing_count,
            dayun=dayun,
            dayun_start=dayun_start,
            dayun_forward=dayun_forward,
            meta={
                "rules": self.rules.as_meta(),
                "inputLabel": f"{calendar_label}{leap_label} {input_label}",
                "calendarType": data.calendar_type,
            },
            pillar_detail=pillar_detail,
            luck_timeline=luck_timeline,
        )

    def _build_pillars(self, ec) -> dict[str, Pillar]:
        getters = {
            "year": (
                ec.getYear,
                ec.getYearGan,
                ec.getYearZhi,
                ec.getYearWuXing,
                ec.getYearNaYin,
                ec.getYearHideGan,
                ec.getYearShiShenGan,
                ec.getYearShiShenZhi,
            ),
            "month": (
                ec.getMonth,
                ec.getMonthGan,
                ec.getMonthZhi,
                ec.getMonthWuXing,
                ec.getMonthNaYin,
                ec.getMonthHideGan,
                ec.getMonthShiShenGan,
                ec.getMonthShiShenZhi,
            ),
            "day": (
                ec.getDay,
                ec.getDayGan,
                ec.getDayZhi,
                ec.getDayWuXing,
                ec.getDayNaYin,
                ec.getDayHideGan,
                ec.getDayShiShenGan,
                ec.getDayShiShenZhi,
            ),
            "hour": (
                ec.getTime,
                ec.getTimeGan,
                ec.getTimeZhi,
                ec.getTimeWuXing,
                ec.getTimeNaYin,
                ec.getTimeHideGan,
                ec.getTimeShiShenGan,
                ec.getTimeShiShenZhi,
            ),
        }

        pillars: dict[str, Pillar] = {}
        for key, (
            _full,
            gan_fn,
            zhi_fn,
            wx_fn,
            ny_fn,
            hide_fn,
            sg_fn,
            sz_fn,
        ) in getters.items():
            gan = gan_fn()
            zhi = zhi_fn()
            wx = wx_fn() or ""
            pillars[key] = Pillar(
                gan=gan,
                zhi=zhi,
                gan_wuxing=wx[0] if len(wx) >= 1 else "",
                zhi_wuxing=wx[1] if len(wx) >= 2 else "",
                nayin=ny_fn(),
                hide_gan=list(hide_fn()),
                shishen_gan="" if key == "day" else sg_fn(),
                shishen_zhi=list(sz_fn()),
            )
        return pillars

    def _count_wuxing(self, pillars: dict[str, Pillar]) -> dict[str, int]:
        counts = {k: 0 for k in WUXING_KEYS}
        for pillar in pillars.values():
            if pillar.gan_wuxing in counts:
                counts[pillar.gan_wuxing] += 1
            if pillar.zhi_wuxing in counts:
                counts[pillar.zhi_wuxing] += 1
        return counts

    def _build_dayun(
        self, ec, gender: int, birth_year: int
    ) -> tuple[list[DayunItem], dict[str, int], bool]:
        yun = ec.getYun(gender)
        start = {
            "year": yun.getStartYear(),
            "month": yun.getStartMonth(),
            "day": yun.getStartDay(),
            "hour": yun.getStartHour(),
        }
        items: list[DayunItem] = []
        da_yun = yun.getDaYun()
        for idx, dy in enumerate(da_yun):
            ganzhi = dy.getGanZhi()
            if not ganzhi:
                continue
            start_age = dy.getStartAge()
            end_age = dy.getEndAge()
            items.append(
                DayunItem(
                    index=idx,
                    ganzhi=ganzhi,
                    start_age=start_age,
                    end_age=end_age,
                    start_year=birth_year + start_age,
                )
            )
        return items, start, yun.isForward()
