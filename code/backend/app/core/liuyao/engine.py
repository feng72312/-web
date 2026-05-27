from __future__ import annotations

from app.core.liuyao.calendar_ctx import calendar_for_chart
from app.core.liuyao.casting import cast_lines
from app.core.liuyao.hexagram import (
    build_changed_lines,
    hexagram_from_lines,
    moving_line_positions,
)
from app.core.liuyao.liushen import liushen_for_day
from app.core.liuyao.models import GuaInfo, LiuyaoChart, LiuyaoInput, LiuyaoLine
from app.core.liuyao.najia import liuqin_for_branch, najia_stems_branches
from app.core.liuyao.trigrams import PALACE_ELEMENT


class LiuyaoEngine:
    """Deterministic Liu Yao chart builder (正宗纳甲装卦)."""

    def divine(self, data: LiuyaoInput) -> LiuyaoChart:
        line_values, cast_note = cast_lines(data)
        calendar = calendar_for_chart(data)
        ben = self._build_gua_chart(line_values, calendar)
        changed_values = build_changed_lines(line_values)
        bian = None
        if changed_values is not None:
            bian = self._build_gua_info(changed_values)

        return LiuyaoChart(
            input=data,
            ben_gua=ben["info"],
            bian_gua=bian,
            lines=ben["lines"],
            moving_lines=moving_line_positions(line_values),
            shi_ying={"shi": ben["shi"], "ying": ben["ying"]},
            month_jian=calendar["monthJian"],
            day_chen=calendar["dayChen"],
            day_gan=calendar["dayGan"],
            meta={
                "rules": "卜筮正宗纳甲",
                "castNote": cast_note,
                "lineValues": line_values,
            },
        )

    def _build_gua_chart(self, line_values: list[int], calendar: dict[str, str]) -> dict:
        name, lower, upper, palace, shi, ying = hexagram_from_lines(line_values)
        info = GuaInfo(
            name=name,
            lower=lower,
            upper=upper,
            palace=palace,
            palace_element=PALACE_ELEMENT[palace],
        )
        lines = self._build_lines(
            line_values,
            lower,
            upper,
            palace,
            shi,
            ying,
            calendar["dayGan"],
        )
        return {"info": info, "lines": lines, "shi": shi, "ying": ying}

    def _build_gua_info(self, line_values: list[int]) -> GuaInfo:
        name, lower, upper, palace, _, _ = hexagram_from_lines(line_values)
        return GuaInfo(
            name=name,
            lower=lower,
            upper=upper,
            palace=palace,
            palace_element=PALACE_ELEMENT[palace],
        )

    def _build_lines(
        self,
        line_values: list[int],
        lower: str,
        upper: str,
        palace: str,
        shi: int,
        ying: int,
        day_gan: str,
    ) -> list[LiuyaoLine]:
        stems_branches = najia_stems_branches(lower, upper)
        liushen = liushen_for_day(day_gan)
        lines: list[LiuyaoLine] = []
        for idx, value in enumerate(line_values):
            stem, branch = stems_branches[idx]
            lines.append(
                LiuyaoLine(
                    position=idx + 1,
                    value=value,
                    is_moving=value in (6, 9),
                    is_yang=value in (7, 9),
                    branch=branch,
                    stem=stem,
                    liuqin=liuqin_for_branch(palace, branch),
                    liushen=liushen[idx],
                    is_shi=idx + 1 == shi,
                    is_ying=idx + 1 == ying,
                )
            )
        return lines
