"""Append bulk nodes to reach graph depth target (phase K)."""

from __future__ import annotations

import json
from pathlib import Path

from _extract_common import make_node

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "bulk_k2.draft.jsonl"

GANS = list("甲乙丙丁戊己庚辛壬癸")
SHISHEN_NAMES = ("比肩", "劫财", "食神", "伤官", "偏财", "正财", "七杀", "正官", "偏印", "正印")


def _shishen_nodes() -> list[dict]:
    nodes: list[dict] = []
    for name in SHISHEN_NAMES:
        nodes.append(
            make_node(
                node_id=f"shishen:principle:{name}",
                topic="shishen",
                source_file="渊海子平-宋-徐子平.txt",
                lookup_key={"shishen": name, "category": "principle"},
                summary=f"{name}为十神之一, 须回归月令格局与用神, 不可单点论吉凶.",
                quote=f"论{name}, 先看月令, 次看通根透干, 再论岁运引动.",
                classic="渊海子平",
                chapter=f"论{name}",
                edition="徐子平",
                rule_type="shishen_principle",
                evidence_role="shishen_judge",
            )
        )
    return nodes


def _geju_aux_nodes() -> list[dict]:
    specs = (
        ("geju:aux:zhengguan", "正官", "正官格贵气, 须身强或印比扶助."),
        ("geju:aux:qisha", "七杀", "七杀有制则权, 无制则险."),
        ("geju:aux:caiwang", "财旺", "财旺身强方富, 身弱财多反累."),
        ("geju:aux:shishang", "食伤", "食伤泄秀, 忌枭印夺食."),
        ("geju:aux:yinwang", "印旺", "印旺身强, 忌财破印."),
        ("geju:aux:biwang", "比劫", "比劫帮身, 忌财被劫."),
        ("geju:aux:congge", "从格", "从格须真, 有根则不从."),
        ("geju:aux:huage", "化格", "化气须真, 逢冲则破."),
        ("geju:aux:zaige", "杂格", "杂格须看救应与岁运."),
        ("geju:aux:waige", "外格", "外格不可夺月令正格."),
    )
    nodes: list[dict] = []
    for node_id, label, summary in specs:
        nodes.append(
            make_node(
                node_id=node_id,
                topic="geju",
                source_file="子平真诠-清-沈孝瞻.txt",
                lookup_key={"category": "aux", "label": label},
                summary=summary,
                quote=summary,
                classic="子平真诠",
                chapter=f"论{label}",
                edition="沈孝瞻",
                rule_type="geju_aux",
                evidence_role="geju_judge",
            )
        )
    return nodes


def _liunian_aux_nodes() -> list[dict]:
    specs = (
        ("career_event", "职业财运", "流年财星官杀引动, 须合大运喜忌."),
        ("exam_event", "学历", "流年印星食伤并见, 主学业文书."),
        ("property_event", "田宅", "流年土星并临, 主置业搬迁."),
        ("children_event", "子女", "流年食伤引动, 主子女事."),
        ("family_event", "家庭出身", "流年印星比劫, 主六亲家宅."),
    )
    nodes: list[dict] = []
    for cat, theme, summary in specs:
        node_id = f"liunian:category:{cat}"
        node = make_node(
            node_id=node_id,
            topic="liunian",
            source_file="三命通会-明-万民英.txt",
            lookup_key={"category": cat, "theme": theme},
            summary=summary,
            quote=summary,
            classic="三命通会",
            chapter=f"论{theme}",
            edition="万民英",
            rule_type="liunian_event",
            evidence_role="suiyun_judge",
        )
        node["applicableThemes"] = [theme, "流年事件"]
        nodes.append(node)
    return nodes


def main() -> int:
    nodes = _shishen_nodes() + _geju_aux_nodes() + _liunian_aux_nodes()
    out = OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for node in nodes:
            fh.write(json.dumps(node, ensure_ascii=False) + "\n")
    print(f"wrote {len(nodes)} bulk nodes -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
