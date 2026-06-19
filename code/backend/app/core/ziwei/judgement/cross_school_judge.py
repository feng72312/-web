from __future__ import annotations

from typing import Any

from app.core.ziwei.judgement._helpers import chart_school
from app.core.ziwei.judgement.models import ZiweiJudgeVerdict


class CrossSchoolJudge:
    def judge(self, chart: dict[str, Any], *, school: str | None = None) -> ZiweiJudgeVerdict:
        active = school or chart_school(chart)
        other = "feixing" if active == "sanhe" else "sanhe"
        flying_present = any(
            (palace.get("flyingMutagens") or {}).get("outbound")
            for palace in chart.get("palaces") or []
        )

        if active == "feixing":
            summary = "主裁法派: 飞星派, 以宫干四化方向与冲照为主"
            if flying_present:
                summary += ", 已检出飞化链路"
            else:
                summary += ", 飞化数据不足时降置信度"
        else:
            summary = "主裁法派: 三合派, 以星曜庙旺与三方四正组合为主"
            if flying_present:
                summary += "; 飞星视角作 schoolCommentary 辅助"

        return ZiweiJudgeVerdict(
            role="cross_school",
            classic="太微赋",
            summary=summary,
            stance="neutral",
            ruleIds=[f"school:{active}", f"school:alt:{other}"],
            confidenceBand="medium",
            flags={"primarySchool": active, "alternateSchool": other, "flyingPresent": flying_present},
            boundary=f"未声明法派时默认{active}, 另一派({other})仅辅助",
        )
