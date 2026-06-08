from __future__ import annotations

from app.core.hepan.models import HepanDiscipline, HepanScene, ResolvedDiscipline

SCENE_DEFAULT_DISCIPLINE: dict[HepanScene, ResolvedDiscipline] = {
    "romance": "ziwei",
    "marriage": "ziwei",
    "partnership": "bazi",
}

SCENE_DEFAULT_QUESTION: dict[HepanScene, str] = {
    "romance": "\u8bf7\u8bba\u4e24\u4eba\u604b\u7231\u7f18\u5206\u4e0e\u76f8\u5904\u8981\u70b9",
    "marriage": "\u8bf7\u8bba\u4e24\u4eba\u5a5a\u59fb\u5951\u5408\u5ea6\u4e0e\u957f\u671f\u7a33\u5b9a\u6027",
    "partnership": "\u8bf7\u8bba\u4e24\u4eba\u5546\u4e1a\u5408\u4f5c\u4e92\u8865\u6027\u4e0e\u98ce\u9669",
}

SCENE_LABELS: dict[HepanScene, str] = {
    "romance": "\u604b\u7231",
    "marriage": "\u5a5a\u59fb",
    "partnership": "\u5408\u4f5c",
}


def resolve_discipline(scene: HepanScene, discipline: HepanDiscipline) -> ResolvedDiscipline:
    if discipline in ("bazi", "ziwei"):
        return discipline
    return SCENE_DEFAULT_DISCIPLINE[scene]


def resolve_question(scene: HepanScene, question: str) -> str:
    q = (question or "").strip()
    if q:
        return q
    return SCENE_DEFAULT_QUESTION[scene]
