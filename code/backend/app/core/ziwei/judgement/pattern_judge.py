from __future__ import annotations

from typing import Any

from app.core.ziwei.judgement._helpers import (
    palace_map,
    resolve_palace,
    stars_in_palaces,
)
from app.core.ziwei.judgement.models import EvidenceRequest, ZiweiJudgeVerdict

PATTERN_DEFS: list[dict[str, Any]] = [
    {
        "id": "pattern:sha_po_lang",
        "name": "杀破狼",
        "stars": {"七杀", "破军", "贪狼"},
        "palaces": ["命宫", "迁移", "财帛", "官禄"],
        "classic": "紫微斗数全书",
    },
    {
        "id": "pattern:fu_xiang",
        "name": "府相朝垣",
        "stars": {"天府", "天相"},
        "palaces": ["命宫", "财帛", "官禄", "迁移"],
        "classic": "太微赋",
    },
    {
        "id": "pattern:ji_yue_tong_liang",
        "name": "机月同梁",
        "stars": {"天机", "太阴", "天同", "天梁"},
        "palaces": ["命宫", "迁移", "财帛", "官禄"],
        "classic": "大德山人",
    },
    {
        "id": "pattern:ri_yue",
        "name": "日月并明",
        "stars": {"太阳", "太阴"},
        "palaces": ["命宫", "迁移", "财帛", "官禄"],
        "classic": "太微赋",
    },
    {
        "id": "pattern:zi_fu",
        "name": "紫府同宫",
        "stars": {"紫微", "天府"},
        "palaces": ["命宫", "迁移", "财帛", "官禄"],
        "classic": "太微赋",
    },
]


class PatternJudge:
    def judge(self, chart: dict[str, Any]) -> ZiweiJudgeVerdict:
        pmap = palace_map(chart)
        matched: list[str] = []
        rule_ids: list[str] = []
        flags: dict[str, Any] = {}

        for pattern in PATTERN_DEFS:
            found = stars_in_palaces(pmap, pattern["palaces"])
            required = set(pattern["stars"])
            if required.issubset(found):
                matched.append(pattern["name"])
                rule_ids.append(pattern["id"])
                flags[pattern["id"]] = {"starsFound": sorted(required)}

        if not matched:
            soul = resolve_palace(pmap, "命宫") or {}
            soul_stars = {
                str(star.get("name") or "")
                for star in soul.get("majorStars") or []
                if star.get("name")
            }
            if "破军" in soul_stars and not {"七杀", "贪狼"}.intersection(
                stars_in_palaces(pmap, ["命宫", "迁移", "财帛", "官禄"])
            ):
                return ZiweiJudgeVerdict(
                    role="pattern",
                    classic="紫微格局研究",
                    summary="命宫见破军但杀贪未入命迁财官相关位置, 不成立杀破狼格局",
                    stance="neutral",
                    ruleIds=["pattern:sha_po_lang_reject"],
                    confidenceBand="medium",
                    boundary="单星名称不得替代格局成立校验",
                )
            return ZiweiJudgeVerdict(
                role="pattern",
                classic="紫微格局研究",
                summary="未命中结构化格局节点, 须参星曜组合与四化再论",
                stance="neutral",
                ruleIds=["pattern:none"],
                confidenceBand="weak",
            )

        return ZiweiJudgeVerdict(
            role="pattern",
            classic="紫微格局研究",
            summary=f"命中格局: {'、'.join(matched)}",
            stance="favorable" if len(matched) == 1 else "mixed",
            ruleIds=rule_ids,
            confidenceBand="strong" if matched else "medium",
            flags=flags,
        )

    def evidence_request(self, chart: dict[str, Any], verdict: ZiweiJudgeVerdict) -> EvidenceRequest:
        names = []
        for rule_id in verdict.ruleIds:
            if rule_id.startswith("pattern:"):
                names.append(rule_id.split(":", 1)[1])
        query = " ".join(f"紫微格局{name}" for name in names[:3]) or "紫微格局"
        return EvidenceRequest(
            ruleId=verdict.ruleIds[0] if verdict.ruleIds else "pattern:general",
            topic="pattern",
            query=query,
            classicWhitelist=["紫微格局研究", "太微赋"],
        )
