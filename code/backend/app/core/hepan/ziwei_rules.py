from __future__ import annotations

from typing import Any

from app.core.hepan.constants import SCENE_PALACE_PAIRS, SHA_STAR_NAMES
from app.core.hepan.models import HepanNoteLevel, HepanScene
from app.core.paipan.interactions import ZHI_CHONG, ZHI_HE


def _make_note(
    note_id: str,
    level: HepanNoteLevel,
    dimension: str,
    title: str,
    detail: str,
) -> dict[str, Any]:
    return {
        "id": note_id,
        "level": level,
        "dimension": dimension,
        "title": title,
        "detail": detail,
        "source": "ziwei",
    }


def _palace_by_name(chart: dict[str, Any], name: str) -> dict[str, Any] | None:
    for palace in chart.get("palaces") or []:
        if palace.get("name") == name:
            return palace
    return None


def _major_star_summary(palace: dict[str, Any] | None) -> str:
    if not palace:
        return "\u65e0"
    stars = palace.get("majorStars") or []
    if not stars:
        return "\u65e0\u4e3b\u661f"
    parts: list[str] = []
    for star in stars:
        name = star.get("name", "")
        bright = star.get("brightness") or ""
        if name:
            parts.append(f"{name}({bright})" if bright else name)
    return "\u3001".join(parts) if parts else "\u65e0\u4e3b\u661f"


def _brightness_level(palace: dict[str, Any] | None) -> HepanNoteLevel:
    if not palace:
        return "neutral"
    stars = palace.get("majorStars") or []
    if not stars:
        return "neutral"
    bright_text = " ".join(str(s.get("brightness") or "") for s in stars)
    if any(k in bright_text for k in ("\u5e99", "\u65fa", "\u5f97")):
        return "fit"
    if any(k in bright_text for k in ("\u9677", "\u4e0d")):
        return "caution"
    return "neutral"


def _sha_in_palace(palace: dict[str, Any] | None) -> list[str]:
    if not palace:
        return []
    found: list[str] = []
    for group in ("majorStars", "minorStars", "adjectiveStars"):
        for star in palace.get(group) or []:
            name = star.get("name", "")
            if name in SHA_STAR_NAMES:
                found.append(name)
    return found


def _zhi_relation(zhi_a: str, zhi_b: str) -> str | None:
    if not zhi_a or not zhi_b:
        return None
    for a, b in ZHI_HE:
        if {zhi_a, zhi_b} == {a, b}:
            return "\u5408"
    for a, b in ZHI_CHONG:
        if {zhi_a, zhi_b} == {a, b}:
            return "\u51b2"
    return None


def _palace_pair_note(
    chart_a: dict[str, Any],
    chart_b: dict[str, Any],
    palace_a: str,
    palace_b: str,
    *,
    prefix: str,
    label_a: str = "\u7532",
    label_b: str = "\u4e59",
) -> dict[str, Any] | None:
    pa = _palace_by_name(chart_a, palace_a)
    pb = _palace_by_name(chart_b, palace_b)
    if not pa and not pb:
        return None
    stars_a = _major_star_summary(pa)
    stars_b = _major_star_summary(pb)
    level = _brightness_level(pa)
    detail = (
        f"{label_a}{palace_a}({stars_a}) \u5bf9 {label_b}{palace_b}({stars_b})."
    )
    return _make_note(
        f"ziwei_{prefix}_{palace_a}_{palace_b}",
        level,
        "palace",
        f"{label_a}{palace_a}\u53c2{label_b}{palace_b}",
        detail,
    )


def build_ziwei_cross_notes(
    chart_a: dict[str, Any],
    chart_b: dict[str, Any],
    scene: HepanScene,
) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []

    pairs = SCENE_PALACE_PAIRS.get(scene, SCENE_PALACE_PAIRS["marriage"])
    seen_ids: set[str] = set()
    for palace_a, palace_b in pairs:
        note = _palace_pair_note(
            chart_a,
            chart_b,
            palace_a,
            palace_b,
            prefix="ab",
        )
        if note and note["id"] not in seen_ids:
            seen_ids.add(note["id"])
            notes.append(note)
        reverse = _palace_pair_note(
            chart_b,
            chart_a,
            palace_b,
            palace_a,
            prefix="ba",
            label_a="\u4e59",
            label_b="\u7532",
        )
        if reverse and reverse["id"] not in seen_ids:
            seen_ids.add(reverse["id"])
            notes.append(reverse)

    spouse_a = _palace_by_name(chart_a, "\u592b\u59bb")
    spouse_b = _palace_by_name(chart_b, "\u592b\u59bb")
    for side, palace, label in (
        ("a", spouse_a, "\u7532"),
        ("b", spouse_b, "\u4e59"),
    ):
        level = _brightness_level(palace)
        if palace:
            notes.append(
                _make_note(
                    f"ziwei_spouse_brightness_{side}",
                    level,
                    "star",
                    f"{label}\u592b\u59bb\u5bab\u4e3b\u661f",
                    _major_star_summary(palace),
                )
            )
        sha = _sha_in_palace(palace)
        if sha:
            notes.append(
                _make_note(
                    f"ziwei_spouse_sha_{side}",
                    "caution",
                    "star",
                    f"{label}\u592b\u59bb\u5bab\u6709\u715e",
                    "\u3001".join(sha),
                )
            )

    soul_a = _palace_by_name(chart_a, "\u547d\u5bab")
    soul_b = _palace_by_name(chart_b, "\u547d\u5bab")
    if soul_a and soul_b:
        notes.append(
            _make_note(
                "ziwei_soul_compatibility",
                _brightness_level(soul_a),
                "palace",
                "\u547d\u5bab\u4e92\u53c2",
                f"\u7532\u547d\u5bab: {_major_star_summary(soul_a)}; "
                f"\u4e59\u547d\u5bab: {_major_star_summary(soul_b)}.",
            )
        )

    if spouse_a and soul_b:
        zhi_a = spouse_a.get("earthlyBranch", "")
        zhi_b = soul_b.get("earthlyBranch", "")
        rel = _zhi_relation(zhi_a, zhi_b)
        if rel:
            level: HepanNoteLevel = "fit" if rel == "\u5408" else "caution"
            notes.append(
                _make_note(
                    "ziwei_palace_branch_relation",
                    level,
                    "branch",
                    f"\u7532\u592b\u59bb{zhi_a}\u4e59\u547d{zhi_b}{rel}",
                    f"\u5bab\u4f4d\u5730\u652f{zhi_a}\u4e0e{zhi_b}{rel}.",
                )
            )

    return notes
