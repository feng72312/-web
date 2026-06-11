from __future__ import annotations

import hashlib
import json
from typing import Any

from app.config import settings
from app.core.analysis.registry import AnalysisRegistry
from app.core.hepan.bazi_rules import build_bazi_cross_notes
from app.core.hepan.models import HepanChartResult, HepanPersonCharts
from app.core.hepan.scene import resolve_discipline, resolve_question
from app.core.hepan.tags import build_summary_tags
from app.core.hepan.ziwei_rules import build_ziwei_cross_notes
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.models import PaipanInput
from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import rules_from_payload
from app.schemas.hepan import HepanChartRequest, HepanPersonRequest
from app.schemas.paipan import PaipanRequest
from app.schemas.ziwei import ZiweiChartRequest, ZiweiRulesPayload


def _person_input_key(person: HepanPersonRequest) -> str:
    payload = person.model_dump()
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def same_person(a: HepanPersonRequest, b: HepanPersonRequest) -> bool:
    return _person_input_key(a) == _person_input_key(b)


def person_to_paipan(person: HepanPersonRequest) -> PaipanRequest:
    return PaipanRequest(**person.model_dump())


def person_to_ziwei(
    person: HepanPersonRequest,
    *,
    question: str,
    use_true_solar: bool,
    longitude: float,
    target_year: int | None,
    rules: ZiweiRulesPayload,
) -> ZiweiChartRequest:
    data = person.model_dump()
    data.update(
        {
            "useTrueSolarTime": use_true_solar,
            "longitude": longitude,
            "targetYear": target_year,
            "question": question,
            "rules": rules,
        }
    )
    return ZiweiChartRequest(**data)


def _paipan_input(body: PaipanRequest) -> PaipanInput:
    return PaipanInput(
        name=body.name.strip(),
        calendar_type=body.calendarType,
        year=body.year,
        month=body.month,
        day=body.day,
        is_leap_month=body.isLeapMonth,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        gender=body.gender,
    )


def build_bazi_chart(
    person: HepanPersonRequest,
    engine: PaipanEngine,
    registry: AnalysisRegistry,
) -> dict[str, Any]:
    req = person_to_paipan(person)
    result = engine.calculate(_paipan_input(req), include_luck_timeline=False)
    chart = result.to_dict()
    chart["sections"] = registry.run_all(chart)
    return chart


def _ziwei_input(body: ZiweiChartRequest) -> ZiweiInput:
    rules = rules_from_payload(
        body.rules.model_dump(),
        default_leap=settings.ziwei_leap_month_rule,
        default_zi=settings.ziwei_zi_hour_rule,
        default_mutagen=settings.ziwei_mutagen_table,
    )
    return ZiweiInput(
        name=body.name,
        calendar_type=body.calendarType,  # type: ignore[arg-type]
        year=body.year,
        month=body.month,
        day=body.day,
        is_leap_month=body.isLeapMonth,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        gender=body.gender,
        use_true_solar_time=body.useTrueSolarTime,
        longitude=body.longitude,
        target_year=body.targetYear,
        detail_level=body.detailLevel,
        question=body.question,
        rules=rules,
    )


def build_ziwei_chart(body: ZiweiChartRequest, engine: ZiweiEngine) -> dict[str, Any]:
    return engine.chart(_ziwei_input(body)).to_dict()


class HepanService:
    def __init__(
        self,
        bazi_engine: PaipanEngine,
        ziwei_engine: ZiweiEngine,
        registry: AnalysisRegistry,
    ) -> None:
        self._bazi_engine = bazi_engine
        self._ziwei_engine = ziwei_engine
        self._registry = registry

    def build_charts(self, body: HepanChartRequest) -> HepanChartResult:
        if same_person(body.personA, body.personB):
            raise ValueError("\u5408\u76d8\u9700\u8981\u4e24\u4e2a\u4e0d\u540c\u547d\u76d8")

        scene = body.scene
        discipline = resolve_discipline(scene, body.discipline)
        question = resolve_question(scene, body.question)

        bazi_a = build_bazi_chart(body.personA, self._bazi_engine, self._registry)
        bazi_b = build_bazi_chart(body.personB, self._bazi_engine, self._registry)

        ziwei_a: dict[str, Any] | None = None
        ziwei_b: dict[str, Any] | None = None
        if discipline == "ziwei":
            ziwei_req_a = person_to_ziwei(
                body.personA,
                question=question,
                use_true_solar=body.useTrueSolarTime,
                longitude=body.longitude,
                target_year=body.targetYear,
                rules=body.ziweiRules,
            )
            ziwei_req_b = person_to_ziwei(
                body.personB,
                question=question,
                use_true_solar=body.useTrueSolarTime,
                longitude=body.longitude,
                target_year=body.targetYear,
                rules=body.ziweiRules,
            )
            ziwei_a = build_ziwei_chart(ziwei_req_a, self._ziwei_engine)
            ziwei_b = build_ziwei_chart(ziwei_req_b, self._ziwei_engine)

        if discipline == "bazi":
            cross_notes = build_bazi_cross_notes(bazi_a, bazi_b, scene)
        else:
            assert ziwei_a is not None and ziwei_b is not None
            cross_notes = build_ziwei_cross_notes(ziwei_a, ziwei_b, scene)

        person_a = HepanPersonCharts(
            name=body.personA.name or "\u7532",
            gender=body.personA.gender,
            bazi_chart=bazi_a,
            ziwei_chart=ziwei_a,
        )
        person_b = HepanPersonCharts(
            name=body.personB.name or "\u4e59",
            gender=body.personB.gender,
            bazi_chart=bazi_b,
            ziwei_chart=ziwei_b,
        )

        return HepanChartResult(
            scene=scene,
            discipline=discipline,
            person_a=person_a,
            person_b=person_b,
            cross_notes=cross_notes,
            summary_tags=build_summary_tags(cross_notes),
            question=question,
        )

    @staticmethod
    def chart_key(hepan: dict[str, Any]) -> str:
        payload = {
            "personA": (hepan.get("personA") or {}).get("baziChart", {}).get("input"),
            "personB": (hepan.get("personB") or {}).get("baziChart", {}).get("input"),
            "scene": hepan.get("scene"),
            "discipline": hepan.get("discipline"),
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
