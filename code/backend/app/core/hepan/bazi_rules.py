from __future__ import annotations

from typing import Any

from app.core.hepan.constants import (
    GAN_WUXING,
    PILLAR_KEYS,
    SPOUSE_SHISHEN,
    WUXING_KE,
    WUXING_SHENG,
)
from app.core.hepan.models import HepanScene, HepanNoteLevel
from app.core.paipan.interactions import GAN_HE, ZHI_CHONG, ZHI_HAI, ZHI_HE


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
        "source": "bazi",
    }


def _find_gan_relation(gan_a: str, gan_b: str) -> list[str]:
    notes: list[str] = []
    for a, b in GAN_HE:
        if {gan_a, gan_b} == {a, b}:
            notes.append("\u5408")
    wx_a = GAN_WUXING.get(gan_a, "")
    wx_b = GAN_WUXING.get(gan_b, "")
    if wx_a and wx_b:
        if WUXING_KE.get(wx_a) == wx_b:
            notes.append("\u514b")
        elif WUXING_KE.get(wx_b) == wx_a:
            notes.append("\u88ab\u514b")
        elif WUXING_SHENG.get(wx_a) == wx_b:
            notes.append("\u751f")
        elif WUXING_SHENG.get(wx_b) == wx_a:
            notes.append("\u88ab\u751f")
        elif wx_a == wx_b:
            notes.append("\u540c")
    return notes


def _find_zhi_relations(zhi_a: str, zhi_b: str) -> list[str]:
    relations: list[str] = []
    for a, b in ZHI_HE:
        if {zhi_a, zhi_b} == {a, b}:
            relations.append("\u5408")
    for a, b in ZHI_CHONG:
        if {zhi_a, zhi_b} == {a, b}:
            relations.append("\u51b2")
    for a, b in ZHI_HAI:
        if {zhi_a, zhi_b} == {a, b}:
            relations.append("\u5bb3")
    return relations


def _pillars(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return chart.get("pillars") or {}


def _collect_shishen_hits(chart: dict[str, Any], targets: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    pillars = _pillars(chart)
    for key in PILLAR_KEYS:
        p = pillars.get(key) or {}
        gan_ss = p.get("shishenGan") or ""
        if gan_ss in targets:
            hits.append(f"{key}\u67f1\u5929\u5e72{gan_ss}")
        for idx, hide in enumerate(p.get("hideGan") or []):
            zhi_ss = (p.get("shishenZhi") or [])
            label = zhi_ss[idx] if idx < len(zhi_ss) else ""
            if label in targets:
                hits.append(f"{key}\u67f1\u85cf{hide}({label})")
    return hits


def _cross_branch_scan(
    chart_a: dict[str, Any],
    chart_b: dict[str, Any],
    *,
    skip_day_pair: bool = True,
) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    zhis_a = {k: (_pillars(chart_a).get(k) or {}).get("zhi", "") for k in PILLAR_KEYS}
    zhis_b = {k: (_pillars(chart_b).get(k) or {}).get("zhi", "") for k in PILLAR_KEYS}
    day_a = zhis_a.get("day", "")
    day_b = zhis_b.get("day", "")
    for ka, za in zhis_a.items():
        if not za:
            continue
        for kb, zb in zhis_b.items():
            if not zb:
                continue
            if skip_day_pair and ka == "day" and kb == "day":
                continue
            rels = _find_zhi_relations(za, zb)
            for rel in rels:
                level: HepanNoteLevel = "fit" if rel == "\u5408" else "caution"
                notes.append(
                    _make_note(
                        f"bazi_cross_{ka}_{kb}_{za}_{zb}_{rel}",
                        level,
                        "branch",
                        f"{za}{zb}{rel}",
                        f"\u7532{ka}\u67f1{za} \u4e0e \u4e59{kb}\u67f1{zb} {rel}.",
                    )
                )
    if day_a and day_b and not skip_day_pair:
        pass
    return notes


def _wuxing_complement(chart_a: dict[str, Any], chart_b: dict[str, Any]) -> dict[str, Any] | None:
    count_a = chart_a.get("wuxingCount") or {}
    count_b = chart_b.get("wuxingCount") or {}
    if not count_a or not count_b:
        return None
    elements = ("\u6728", "\u706b", "\u571f", "\u91d1", "\u6c34")
    weak_a = [e for e in elements if int(count_a.get(e, 0)) == 0]
    weak_b = [e for e in elements if int(count_b.get(e, 0)) == 0]
    complement: list[str] = []
    for e in weak_a:
        if int(count_b.get(e, 0)) >= 2:
            complement.append(f"\u7532\u7f3a{e}\u4e59\u65fa")
    for e in weak_b:
        if int(count_a.get(e, 0)) >= 2:
            complement.append(f"\u4e59\u7f3a{e}\u7532\u65fa")
    if not complement:
        return None
    return _make_note(
        "bazi_wuxing_complement",
        "fit",
        "wuxing",
        "\u4e94\u884c\u4e92\u8865",
        "\u3001".join(complement[:4]),
    )


def build_bazi_cross_notes(
    chart_a: dict[str, Any],
    chart_b: dict[str, Any],
    scene: HepanScene,
) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    pillars_a = _pillars(chart_a)
    pillars_b = _pillars(chart_b)
    day_a = pillars_a.get("day") or {}
    day_b = pillars_b.get("day") or {}
    zhi_a = day_a.get("zhi", "")
    zhi_b = day_b.get("zhi", "")
    gan_a = day_a.get("gan", "")
    gan_b = day_b.get("gan", "")

    if zhi_a and zhi_b:
        day_rels = _find_zhi_relations(zhi_a, zhi_b)
        if day_rels:
            rel = day_rels[0]
            level: HepanNoteLevel = "fit" if rel == "\u5408" else "caution"
            marriage_hint = (
                "\u5408\u62a5\u6709\u5229" if rel == "\u5408" else "\u9700\u6ce8\u610f\u51b2\u7a81"
            )
            notes.append(
                _make_note(
                    "bazi_day_zhi_relation",
                    level,
                    "day_pillar",
                    f"\u65e5\u652f{zhi_a}{zhi_b}{rel}",
                    f"\u4e24\u4eba\u65e5\u652f{zhi_a}\u4e0e{zhi_b}{rel}, "
                    f"\u5a5a\u7f18\u5bab{marriage_hint}.",
                )
            )

    if gan_a and gan_b:
        gan_rels = _find_gan_relation(gan_a, gan_b)
        if gan_rels:
            level = "fit" if "\u5408" in gan_rels or "\u751f" in gan_rels else "caution"
            notes.append(
                _make_note(
                    "bazi_day_gan_relation",
                    level,
                    "day_pillar",
                    f"\u65e5\u5e72{gan_a}{gan_b}{''.join(gan_rels)}",
                    f"\u7532\u65e5\u5e72{gan_a}\u4e0e\u4e59\u65e5\u5e72{gan_b}: {','.join(gan_rels)}.",
                )
            )

    dm_a = chart_a.get("dayMaster", "")
    dm_b = chart_b.get("dayMaster", "")
    wx_a = chart_a.get("dayMasterWuxing", "") or GAN_WUXING.get(dm_a, "")
    wx_b = chart_b.get("dayMasterWuxing", "") or GAN_WUXING.get(dm_b, "")
    if wx_a and wx_b:
        if WUXING_SHENG.get(wx_a) == wx_b or WUXING_SHENG.get(wx_b) == wx_a:
            notes.append(
                _make_note(
                    "bazi_day_master_wuxing",
                    "fit",
                    "wuxing",
                    "\u4e3b\u5bb9\u4e94\u884c\u76f8\u751f",
                    f"\u7532\u4e3b{dm_a}({wx_a}) \u4e0e \u4e59\u4e3b{dm_b}({wx_b}) \u76f8\u751f\u6709\u52a9.",
                )
            )
        elif WUXING_KE.get(wx_a) == wx_b or WUXING_KE.get(wx_b) == wx_a:
            notes.append(
                _make_note(
                    "bazi_day_master_wuxing",
                    "caution",
                    "wuxing",
                    "\u4e3b\u5bb9\u4e94\u884c\u76f8\u514b",
                    f"\u7532\u4e3b{dm_a}({wx_a}) \u4e0e \u4e59\u4e3b{dm_b}({wx_b}) \u76f8\u514b, \u76f8\u5904\u9700\u6c42\u540c.",
                )
            )
        elif wx_a == wx_b:
            notes.append(
                _make_note(
                    "bazi_day_master_wuxing",
                    "neutral",
                    "wuxing",
                    "\u4e3b\u5bb9\u540c\u7c7b\u4e94\u884c",
                    f"\u4e24\u4eba\u5747\u4e3a{wx_a}, \u6027\u60c5\u8fd1\u4f3c\u6613\u5171\u9e23\u4ea6\u6613\u540c\u8c28.",
                )
            )

    gender_a = int((chart_a.get("input") or {}).get("gender", 1))
    gender_b = int((chart_b.get("input") or {}).get("gender", 0))
    targets_a = SPOUSE_SHISHEN.get(gender_a, SPOUSE_SHISHEN[1])
    targets_b = SPOUSE_SHISHEN.get(gender_b, SPOUSE_SHISHEN[0])
    hits_a_in_b = _collect_shishen_hits(chart_b, targets_a)
    if hits_a_in_b:
        notes.append(
            _make_note(
                "bazi_spouse_star_a_in_b",
                "fit",
                "spouse",
                "\u7532\u914d\u5076\u661f\u5728\u4e59\u76d8",
                "\u3001".join(hits_a_in_b[:3]),
            )
        )
    hits_b_in_a = _collect_shishen_hits(chart_a, targets_b)
    if hits_b_in_a:
        notes.append(
            _make_note(
                "bazi_spouse_star_b_in_a",
                "fit",
                "spouse",
                "\u4e59\u914d\u5076\u661f\u5728\u7532\u76d8",
                "\u3001".join(hits_b_in_a[:3]),
            )
        )

    notes.extend(_cross_branch_scan(chart_a, chart_b))

    complement = _wuxing_complement(chart_a, chart_b)
    if complement:
        notes.append(complement)

    if scene == "partnership":
        bijie_a = _collect_shishen_hits(chart_a, ("\u6bd4\u80a9", "\u52ab\u8d22"))
        bijie_b = _collect_shishen_hits(chart_b, ("\u6bd4\u80a9", "\u52ab\u8d22"))
        if bijie_a and bijie_b:
            notes.append(
                _make_note(
                    "bazi_partnership_wealth",
                    "caution",
                    "wealth",
                    "\u53cc\u65b9\u6bd4\u52ab\u661f\u663e",
                    "\u4e24\u76d8\u5747\u6709\u6bd4\u52ab/\u52ab\u8d22, \u5408\u4f5c\u9700\u660e\u786e\u5206\u5229\u4e0e\u8d23\u4efb.",
                )
            )
        officer_a = _collect_shishen_hits(chart_a, ("\u6b63\u5b98", "\u4e03\u6740"))
        officer_b = _collect_shishen_hits(chart_b, ("\u6b63\u5b98", "\u4e03\u6740"))
        if officer_a or officer_b:
            notes.append(
                _make_note(
                    "bazi_partnership_officer",
                    "fit",
                    "career",
                    "\u5b98\u6743\u661f\u53ef\u7528",
                    "\u81f3\u5c11\u4e00\u65b9\u5b98\u6740\u6709\u6839, \u5229\u4e8e\u5408\u4f5c\u4e2d\u7684\u89c4\u5219\u4e0e\u6267\u884c.",
                )
            )

    nayin_a = day_a.get("nayin", "")
    nayin_b = day_b.get("nayin", "")
    if nayin_a and nayin_b:
        notes.append(
            _make_note(
                "bazi_nayin_day",
                "neutral",
                "nayin",
                "\u65e5\u67f1\u7eb3\u97f3",
                f"\u7532\u65e5\u67f1\u7eb3\u97f3{nayin_a}, \u4e59\u65e5\u67f1\u7eb3\u97f3{nayin_b}.",
            )
        )

    return notes
