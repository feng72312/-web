"""Extract supplemental liunian nodes from 三命通会."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _extract_common import make_node, read_source_text, trim_summary

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
DEFAULT_SOURCE = ROOT / "数据库" / "01八字命理" / "S_主裁经典" / "三命通会-明-万民英.txt"
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "liunian_sanming.draft.jsonl"

SECTION_RULES: list[tuple[str, str, str]] = [
    ("真太岁", "sanming_zhen_taisui", "论真太岁"),
    ("转趾", "sanming_zhen_taisui", "论真太岁"),
    ("岁运并临", "sanming_suiyun_binglin", "论岁运并临"),
    ("太岁当头", "sanming_taisui_head", "论太岁当头"),
    ("伏吟", "sanming_fuyin", "论伏吟"),
    ("反吟", "sanming_fanyin", "论反吟"),
    ("冲克太岁", "sanming_zhan_chong_he", "论战冲和好"),
    ("日犯岁君", "sanming_zhan_chong_he", "论战冲和好"),
    ("相克相冲", "sanming_zhan_chong_he", "论战冲和好"),
    ("小运", "sanming_xiaoyun", "论小运"),
]


def _pick_quote(raw: str, keyword: str, *, window: int = 420) -> str:
    idx = raw.find(keyword)
    if idx < 0:
        return ""
    start = max(0, idx - 40)
    return raw[start : start + window].strip()


def extract(source_path: Path) -> list[dict]:
    raw = read_source_text(source_path)
    source_file = source_path.name
    nodes: dict[str, dict] = {}

    for keyword, category, chapter in SECTION_RULES:
        quote = _pick_quote(raw, keyword)
        if len(quote) < 50:
            continue
        node_id = f"liunian:{category}"
        if node_id in nodes and len(quote) <= len(nodes[node_id]["claims"][0]["quote"]):
            continue
        summary = trim_summary(quote, 100)
        nodes[node_id] = make_node(
            node_id=node_id,
            topic="liunian",
            source_file=source_file,
            lookup_key={"category": category},
            summary=summary,
            quote=quote,
            classic="三命通会",
            chapter=chapter,
            edition="万民英",
            rule_type="liunian_rule",
            evidence_role="suiyun_judge",
        )

    return list(nodes.values())


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
    print(f"extracted {len(nodes)} liunian sanming nodes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
