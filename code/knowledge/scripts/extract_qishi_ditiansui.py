"""Extract qishi nodes from 滴天髓阐微 into draft JSONL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _extract_common import make_node, read_source_text, trim_summary

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
DEFAULT_SOURCE = ROOT / "数据库" / "01八字命理" / "S_主裁经典" / "滴天髓阐微-清-任铁樵.txt"
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "qishi_ditiansui.draft.jsonl"

WUXING = list("木火土金水")
CHAPTER_KEYS = {
    "旺衰": "wangshuai",
    "中和": "zhonghe",
    "通关": "tongguan",
    "源流": "yuanliu",
    "清气": "qingqi",
    "浊气": "zhuoqi",
    "顺逆": "shunni",
    "寒暖": "hannuan",
    "燥湿": "zaoshi",
    "形象": "xingxiang",
    "方局": "fangju",
    "体用": "tiyong",
}

CHAPTER_RE = re.compile(r"^[一二三四五六七八九十]+、([\u4e00-\u9fff]+)")


def extract(source_path: Path) -> list[dict]:
    raw = read_source_text(source_path)
    source_file = source_path.name
    nodes: list[dict] = []
    current_title = ""
    current_key = ""
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer, current_title, current_key
        if not current_key or not buffer:
            buffer = []
            return
        quote = "\n".join(buffer).strip()
        if len(quote) < 30:
            buffer = []
            return
        node_id = f"qishi:category:{current_key}"
        nodes.append(
            make_node(
                node_id=node_id,
                topic="qishi",
                source_file=source_file,
                lookup_key={"category": current_key, "qishiTopic": current_title},
                summary=trim_summary(quote, 100),
                quote=quote,
                classic="滴天髓",
                chapter=current_title,
                edition="任铁樵",
                rule_type="qishi_flow",
                evidence_role="qishi_judge",
            )
        )
        buffer = []

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            if buffer:
                buffer.append("")
            continue
        chapter_match = CHAPTER_RE.match(stripped)
        if chapter_match:
            title = chapter_match.group(1)
            mapped = None
            for key, value in CHAPTER_KEYS.items():
                if title == key or title.startswith(key):
                    mapped = value
                    break
            if mapped:
                flush()
                current_title = title
                current_key = mapped
                rest = stripped[chapter_match.end() :].strip()
                buffer = [rest] if rest else []
                continue
        if current_key:
            if CHAPTER_RE.match(stripped):
                flush()
                continue
            buffer.append(stripped)

    flush()

    for wx in WUXING:
        pattern = re.compile(rf"([^\n。]{{8,80}}{wx}[^\n。]{{0,40}})")
        hits = pattern.findall(raw)
        if not hits:
            continue
        quote = hits[0]
        node_id = f"qishi:dominant:{wx}"
        nodes.append(
            make_node(
                node_id=node_id,
                topic="qishi",
                source_file=source_file,
                lookup_key={"dominant": wx, "category": "wuxing_bias"},
                summary=trim_summary(quote, 100),
                quote=quote,
                classic="滴天髓",
                chapter=f"五行偏{wx}",
                edition="任铁樵",
                rule_type="qishi_wuxing",
                evidence_role="qishi_judge",
            )
        )

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
    print(f"extracted {len(nodes)} qishi nodes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
