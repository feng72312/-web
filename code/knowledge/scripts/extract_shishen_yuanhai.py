"""Extract shishen nodes from 渊海子平 into draft JSONL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _extract_common import make_node, read_source_text, trim_summary

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
DEFAULT_SOURCE = ROOT / "数据库" / "01八字命理" / "S_主裁经典" / "渊海子平-宋-徐子平.txt"
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "shishen_yuanhai.draft.jsonl"

ENTRY_RE = re.compile(r"见([甲乙丙丁戊己庚辛壬癸])：为([^，,\n]+)")
SHISHEN_NORMALIZE = {
    "比肩": "比肩",
    "劫财": "劫财",
    "败财": "劫财",
    "逐马": "劫财",
    "食神": "食神",
    "伤官": "伤官",
    "正财": "正财",
    "偏财": "偏财",
    "正官": "正官",
    "偏官": "七杀",
    "七杀": "七杀",
    "官鬼": "七杀",
    "印绶": "正印",
    "印綬": "正印",
    "正印": "正印",
    "倒食": "偏印",
    "偏印": "偏印",
    "枭神": "偏印",
    "梟神": "偏印",
}

LIUQIN_SECTIONS: dict[str, tuple[str, list[str], str]] = {
    "general": ("六亲者", ["譬如"], "六亲总则"),
    "male_spouse": ("男命", ["女命"], "男命配偶"),
    "male_parent": ("偏财为父", ["女命"], "男命父母"),
    "female_spouse": ("女命", ["阳干"], "女命配偶"),
    "female_parent": ("女命取", ["阳干"], "女命父母"),
    "children": ("食神为子", ["女命取"], "子女"),
    "sibling": ("比肩为兄弟", ["食神为子"], "兄弟姊妹"),
}

MAX_QUOTE_LEN = 500


def _normalize_shishen(raw: str) -> str:
    text = raw.strip().rstrip("。")
    for key, value in SHISHEN_NORMALIZE.items():
        if key in text:
            return value
    return text.split("、")[0][:6]


def _slice_text(raw: str, start: str, end_markers: list[str]) -> str:
    idx = raw.find(start)
    if idx < 0:
        return ""
    end = len(raw)
    for marker in end_markers:
        pos = raw.find(marker, idx + len(start))
        if pos > idx:
            end = min(end, pos)
    return raw[idx:end].strip()[:MAX_QUOTE_LEN]


def _extract_relation_nodes(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    by_shishen: dict[str, list[str]] = {}

    for day_gan, raw_ss in ENTRY_RE.findall(raw):
        shishen = _normalize_shishen(raw_ss)
        quote = f"见{day_gan}：为{raw_ss}"
        by_shishen.setdefault(shishen, []).append(quote)
        nodes.append(
            make_node(
                node_id=f"shishen:{day_gan}:{shishen}",
                topic="shishen",
                source_file=source_file,
                lookup_key={"dayGan": day_gan, "shishen": shishen},
                summary=trim_summary(quote, 80),
                quote=quote,
                classic="渊海子平",
                chapter=f"日干{day_gan}见{shishen}",
                edition="徐子平",
                rule_type="shishen_relation",
                evidence_role="shishen_judge",
            )
        )

    for shishen, quotes in by_shishen.items():
        quote = "；".join(quotes[:5])
        nodes.append(
            make_node(
                node_id=f"shishen:role:{shishen}",
                topic="shishen",
                source_file=source_file,
                lookup_key={"shishen": shishen, "role": shishen},
                summary=trim_summary(quote, 100),
                quote=quote,
                classic="渊海子平",
                chapter=f"论{shishen}",
                edition="徐子平",
                rule_type="shishen_summary",
                evidence_role="shishen_judge",
            )
        )
    return nodes


def _extract_liuqin_nodes(raw: str, source_file: str) -> list[dict]:
    nodes: list[dict] = []
    for aspect, (start, ends, label) in LIUQIN_SECTIONS.items():
        quote = _slice_text(raw, start, ends)
        if len(quote.strip()) < 20:
            continue
        nodes.append(
            make_node(
                node_id=f"shishen:liuqin:{aspect}",
                topic="shishen",
                source_file=source_file,
                lookup_key={"category": "liuqin", "aspect": aspect},
                summary=trim_summary(quote, 100),
                quote=quote,
                classic="渊海子平",
                chapter=f"论六亲-{label}",
                edition="徐子平",
                rule_type="shishen_liuqin",
                evidence_role="shishen_judge",
            )
        )
    return nodes


def extract(source_path: Path) -> list[dict]:
    raw = read_source_text(source_path)
    source_file = source_path.name
    nodes: list[dict] = []
    nodes.extend(_extract_relation_nodes(raw, source_file))
    nodes.extend(_extract_liuqin_nodes(raw, source_file))

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
    print(f"extracted {len(nodes)} shishen nodes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
