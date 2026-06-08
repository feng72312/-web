from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

HepanScene = Literal["romance", "marriage", "partnership"]
HepanDiscipline = Literal["auto", "bazi", "ziwei"]
HepanNoteLevel = Literal["fit", "caution", "neutral"]
ResolvedDiscipline = Literal["bazi", "ziwei"]


@dataclass
class HepanPersonCharts:
    name: str
    gender: int
    bazi_chart: dict[str, Any] | None = None
    ziwei_chart: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "gender": self.gender,
            "baziChart": self.bazi_chart,
            "ziweiChart": self.ziwei_chart,
        }


@dataclass
class HepanChartResult:
    scene: HepanScene
    discipline: ResolvedDiscipline
    person_a: HepanPersonCharts
    person_b: HepanPersonCharts
    cross_notes: list[dict[str, Any]]
    summary_tags: list[str]
    question: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene": self.scene,
            "discipline": self.discipline,
            "personA": self.person_a.to_dict(),
            "personB": self.person_b.to_dict(),
            "crossNotes": self.cross_notes,
            "summaryTags": self.summary_tags,
            "question": self.question,
        }
