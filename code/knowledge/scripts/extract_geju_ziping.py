"""Extract geju nodes from 子平真诠评注 into draft JSONL (batch 1-4)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _extract_common import make_node, read_source_text, trim_summary

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
DEFAULT_SOURCE = ROOT / "数据库" / "01八字命理" / "S_主裁经典" / "子平真诠评注-清-沈孝瞻.txt"
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "geju_ziping.draft.jsonl"

GEJU_NAMES = ("正官", "正财", "正印", "食神", "七杀", "伤官", "阳刃", "比肩")

PATTERN_SECTIONS: dict[str, tuple[str, list[str]]] = {
    "正官": ("官以克身", ["财为我克"]),
    "正财": ("财为我克", ["印绶喜其生身"]),
    "正印": ("印绶喜其生身", ["食神本属泄气"]),
    "食神": ("食神本属泄气", ["煞以攻身"]),
    "七杀": ("煞以攻身", ["伤官虽非吉神"]),
    "伤官": ("伤官虽非吉神", ["阳刃者"]),
    "阳刃": ("阳刃者", ["建禄者"]),
    "比肩": ("建禄者", ["杂格者"]),
}

YUN_MARKERS: dict[str, str] = {
    "正官": "如正官取运，即以正官所统之格分而配之",
    "正财": "财格取运，即以财格所就之局",
    "正印": "印格取运，即以印格所成之局",
    "食神": "食神取运，即以食神",
    "七杀": "偏官取运，即以偏官",
    "伤官": "伤官取运，即以伤官",
    "比肩": "禄劫取运，即以禄劫",
}

YUN_END_MARKERS: dict[str, list[str]] = {
    "正官": ["财格取运，即以财格"],
    "正财": ["印格取运，即以印格"],
    "正印": ["食神取运，即以食神"],
    "食神": ["偏官取运，即以偏官"],
    "七杀": ["伤官取运，即以伤官"],
    "伤官": ["阳刃者"],
    "比肩": ["杂格者，月令无用"],
}

EXTENDED_PRINCIPLE_SECTIONS: dict[str, tuple[str, list[str]]] = {
    "yongshen": ("论用神", ["月令用神"]),
    "month_yongshen": ("月令用神", ["官以克身"]),
    "mixed_outcome": ("成中有败", ["何谓救应？"]),
}

EXTRA_SPECIAL_SECTIONS: dict[str, tuple[str, list[str]]] = {
    "tongguan": ("（五）通关", ["外格者，盖因月令无用"]),
    "gonglu": ("若夫拱禄", ["财官印食，四吉神也"]),
    "liuqin": ("人有六亲", ["杂格者，月令无用"]),
}

VARIANT_SECTIONS: dict[str, tuple[str, list[str], str, str]] = {
    "正官:peiyin": ("遇伤在于佩印", ["混煞贵乎取清"], "正官", "佩印解伤"),
    "正官:hunsha": ("混煞贵乎取清", ["至于官格透伤用印"], "正官", "混煞取清"),
    "正财:peiyin": ("有财格佩印者", ["有用食而兼用印者"], "正财", "财格佩印"),
    "正财:shishen": ("有财用食生者", ["有财格佩印者"], "正财", "财用食生"),
    "正印:guan": ("有印而透官者", ["然亦有带伤食而贵者"], "正印", "印透官"),
    "食神:zhisha": ("若不用财而就煞印", ["若金水食神而用煞"], "食神", "食就煞印"),
    "七杀:shishen": ("煞用食制者，上也", ["煞用食制，不要露财透印"], "七杀", "煞用食制"),
    "伤官:peiyin": ("伤官佩印", ["伤官生财"], "伤官", "伤官佩印"),
    "伤官:quguan": ("金水伤官可见官之谓也", ["食神而官煞竞出"], "伤官", "金水伤官见官"),
    "比肩:guancai": ("建禄月劫用官", ["建禄月劫用财"], "比肩", "禄劫用官"),
}

ALIAS_GEJU: tuple[tuple[str, str, str], ...] = (
    ("偏财", "正财", "偏财与正财同论一格，子平真诠不分偏正，取格与取运皆依正财例。"),
    ("偏印", "正印", "偏印与正印同论印绶一格，喜其生身，取格与救应皆依正印例。"),
    ("劫财", "比肩", "劫财与比肩同论建禄月劫一格，喜财官煞食配合，依比肩禄劫例。"),
)

PRINCIPLE_SECTIONS: dict[str, tuple[str, list[str]]] = {
    "success": ("何谓成？", ["何谓败？"]),
    "failure": ("何谓败？", ["成中有败", "何谓救应？"]),
    "rescue": ("何谓救应？", ["八字妙用，全在成败救应"]),
    "taboo": ("何谓带忌？", ["成中之败"]),
}

SPECIAL_SECTIONS: dict[str, tuple[str, list[str]]] = {
    "waige": ("外格者，盖因月令无用", ["人有六亲"]),
    "zhuanwang": ("（四）专旺", ["（五）通关"]),
    "zagai": ("杂格者，月令无用", ["试以诸格论之"]),
    "quzhi": ("有取五行一方秀气者", ["有从化取格者"]),
    "huaji": ("有从化取格者", ["有倒冲成格者"]),
    "daochong": ("有倒冲成格者", ["有朝阳成格者"]),
    "chaoyang": ("有朝阳成格者", ["有合禄成格者"]),
    "helu": ("有合禄成格者", ["有弃命保财者"]),
    "congcai": ("有弃命保财者", ["有弃命从煞者"]),
    "congsha": ("有弃命从煞者", ["有井栏成格者"]),
    "jinglan": ("有井栏成格者", ["有刑合成格者"]),
    "xinghe": ("有刑合成格者", ["有遥合成格者"]),
    "yaohe": ("有遥合成格者", ["若夫拱禄"]),
    "jishen_po": ("财官印食，四吉神也", ["煞伤枭刃，四凶神也"]),
    "xionshen_cheng": ("煞伤枭刃，四凶神也", ["月令用神，配以四柱"]),
    "tongguan": ("（五）通关", ["外格者，盖因月令无用"]),
    "gonglu": ("若夫拱禄", ["杂格者，月令无用"]),
    "liuqin": ("人有六亲", ["杂格者，月令无用"]),
}

SPECIAL_LABELS: dict[str, str] = {
    "waige": "外格总则",
    "zhuanwang": "专旺格",
    "zagai": "杂格总则",
    "quzhi": "曲直一方秀气",
    "huaji": "化气格",
    "daochong": "倒冲格",
    "chaoyang": "朝阳格",
    "helu": "合禄格",
    "congcai": "从财格",
    "congsha": "从煞格",
    "jinglan": "井栏叉格",
    "xinghe": "刑合格",
    "yaohe": "遥合格",
    "jishen_po": "四吉神破格",
    "xionshen_cheng": "四凶神成格",
    "tongguan": "通关格",
    "gonglu": "拱禄格",
    "liuqin": "六亲论",
}

MIN_QUOTE_LEN = 40
MAX_QUOTE_LEN = 900


def _slice_text(raw: str, start: str, end_markers: list[str]) -> str:
    idx = raw.find(start)
    if idx < 0:
        return ""
    end = len(raw)
    for marker in end_markers:
        pos = raw.find(marker, idx + len(start))
        if pos > idx:
            end = min(end, pos)
    text = raw[idx:end].strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:MAX_QUOTE_LEN]


def _make_geju_node(
    *,
    node_id: str,
    lookup_key: dict[str, str],
    summary: str,
    quote: str,
    chapter: str,
    source_file: str,
    rule_type: str,
) -> dict | None:
    if len(quote.strip()) < MIN_QUOTE_LEN:
        return None
    return make_node(
        node_id=node_id,
        topic="geju",
        source_file=source_file,
        lookup_key=lookup_key,
        summary=trim_summary(summary, 120),
        quote=quote,
        classic="子平真诠",
        chapter=chapter,
        edition="沈孝瞻",
        rule_type=rule_type,
        evidence_role="geju_judge",
    )


def _extract_principles(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    for aspect, (start, ends) in PRINCIPLE_SECTIONS.items():
        quote = _slice_text(raw, start, ends)
        node = _make_geju_node(
            node_id=f"geju:aspect:{aspect}",
            lookup_key={"aspect": aspect, "category": "geju_outcome"},
            summary=quote[:160],
            quote=quote,
            chapter=f"论用神成败救应-{aspect}",
            source_file=source_file,
            rule_type=f"geju_{aspect}",
        )
        if node:
            nodes.append(node)
    for key, (start, ends) in EXTENDED_PRINCIPLE_SECTIONS.items():
        quote = _slice_text(raw, start, ends)
        node = _make_geju_node(
            node_id=f"geju:principle:{key}",
            lookup_key={"principle": key, "category": "geju_principle"},
            summary=quote[:160],
            quote=quote,
            chapter=f"论格局原则-{key}",
            source_file=source_file,
            rule_type="geju_principle",
        )
        if node:
            nodes.append(node)
    return nodes


def _extract_yun_nodes(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    for geju_name, start in YUN_MARKERS.items():
        ends = YUN_END_MARKERS.get(geju_name, [])
        quote = _slice_text(raw, start, ends)
        node = _make_geju_node(
            node_id=f"geju:month:{geju_name}:yun",
            lookup_key={
                "monthShishen": geju_name,
                "gejuName": geju_name,
                "aspect": "yun",
            },
            summary=quote[:160],
            quote=quote,
            chapter=f"论{geju_name}取运",
            source_file=source_file,
            rule_type="geju_yun",
        )
        if node:
            nodes.append(node)

    yang_start = raw.find("阳刃者")
    yang_end = raw.find("建禄者")
    if yang_start >= 0 and yang_end > yang_start:
        chunk = raw[yang_start:yang_end]
        pos = chunk.rfind("阳刃用官")
        if pos >= 0:
            quote = chunk[pos:].strip()[:MAX_QUOTE_LEN]
            node = _make_geju_node(
                node_id="geju:month:阳刃:yun",
                lookup_key={
                    "monthShishen": "阳刃",
                    "gejuName": "阳刃",
                    "aspect": "yun",
                },
                summary=quote[:160],
                quote=quote,
                chapter="论阳刃取运",
                source_file=source_file,
                rule_type="geju_yun",
            )
            if node:
                nodes.append(node)
    return nodes


def _extract_variant_nodes(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    for key, (start, ends, geju_name, label) in VARIANT_SECTIONS.items():
        quote = _slice_text(raw, start, ends)
        node = _make_geju_node(
            node_id=f"geju:variant:{key}",
            lookup_key={
                "monthShishen": geju_name,
                "gejuName": geju_name,
                "variant": key.split(":", 1)[1],
                "category": "geju_variant",
            },
            summary=quote[:160],
            quote=quote,
            chapter=f"论{geju_name}-{label}",
            source_file=source_file,
            rule_type="geju_variant",
        )
        if node:
            nodes.append(node)
    return nodes


def _extract_alias_nodes(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    for alias, canonical, summary in ALIAS_GEJU:
        quote = summary
        for geju_name, (start, _) in PATTERN_SECTIONS.items():
            if geju_name == canonical:
                excerpt = _slice_text(raw, start, PATTERN_SECTIONS[geju_name][1])
                if excerpt:
                    quote = f"{summary}\n{excerpt[:240]}"
                break
        node = _make_geju_node(
            node_id=f"geju:month:{alias}",
            lookup_key={
                "monthShishen": alias,
                "gejuName": alias,
                "aspect": "core",
                "aliasOf": canonical,
            },
            summary=summary,
            quote=quote[:MAX_QUOTE_LEN],
            chapter=f"论{alias}(同{canonical})",
            source_file=source_file,
            rule_type="geju_pattern_alias",
        )
        if node:
            nodes.append(node)
    return nodes


def _extract_pattern_nodes(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    for geju_name, (start, ends) in PATTERN_SECTIONS.items():
        quote = _slice_text(raw, start, ends)
        node = _make_geju_node(
            node_id=f"geju:month:{geju_name}",
            lookup_key={
                "monthShishen": geju_name,
                "gejuName": geju_name,
                "aspect": "core",
            },
            summary=quote[:160],
            quote=quote,
            chapter=f"论{geju_name}",
            source_file=source_file,
            rule_type="geju_pattern",
        )
        if node:
            nodes.append(node)
    return nodes


def _extract_extra_special_nodes(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    for pattern, (start, ends) in EXTRA_SPECIAL_SECTIONS.items():
        if pattern in SPECIAL_SECTIONS:
            continue
        quote = _slice_text(raw, start, ends)
        label = SPECIAL_LABELS.get(pattern, pattern)
        node = _make_geju_node(
            node_id=f"geju:special:{pattern}",
            lookup_key={"pattern": pattern, "category": "geju_special"},
            summary=quote[:160],
            quote=quote,
            chapter=f"杂格外格-{label}",
            source_file=source_file,
            rule_type="geju_special",
        )
        if node:
            nodes.append(node)
    return nodes


def _extract_special_nodes(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    for pattern, (start, ends) in SPECIAL_SECTIONS.items():
        quote = _slice_text(raw, start, ends)
        label = SPECIAL_LABELS.get(pattern, pattern)
        node = _make_geju_node(
            node_id=f"geju:special:{pattern}",
            lookup_key={"pattern": pattern, "category": "geju_special"},
            summary=quote[:160],
            quote=quote,
            chapter=f"杂格外格-{label}",
            source_file=source_file,
            rule_type="geju_special",
        )
        if node:
            nodes.append(node)
    return nodes


def extract(source_path: Path) -> list[dict]:
    raw = read_source_text(source_path)
    source_file = source_path.name
    nodes: list[dict] = []
    nodes.extend(_extract_principles(raw, source_file))
    nodes.extend(_extract_pattern_nodes(raw, source_file))
    nodes.extend(_extract_yun_nodes(raw, source_file))
    nodes.extend(_extract_variant_nodes(raw, source_file))
    nodes.extend(_extract_alias_nodes(raw, source_file))
    nodes.extend(_extract_special_nodes(raw, source_file))
    nodes.extend(_extract_extra_special_nodes(raw, source_file))

    merged: dict[str, dict] = {}
    for node in nodes:
        merged[node["id"]] = node
    return list(merged.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args()
    source = Path(args.source)
    if not source.exists():
        print(f"source not found: {source}")
        return 1
    nodes = extract(source)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for node in nodes:
            fh.write(json.dumps(node, ensure_ascii=False) + "\n")
    print(f"extracted {len(nodes)} geju nodes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
