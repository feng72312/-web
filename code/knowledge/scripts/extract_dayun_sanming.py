"""Extract dayun nodes from 三命通会 (S-tier) replacing B-tier 命理探源 nodes."""

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
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "dayun_sanming.draft.jsonl"

DAYUN_SPECS = (
    ("dayun:core", "core", ("大运", "行运之地", "十年一运")),
    ("dayun:xingyun_xiji", "xingyun_xiji", ("行运喜忌", "用神在运", "运来克用神")),
    ("dayun:gan_zhi_weight", "gan_zhi_weight", ("大运重地支", "太岁重天干", "运支冲")),
    ("dayun:start_rule", "start_rule", ("起运", "顺逆", "小运")),
    ("dayun:dayun_change", "dayun_change", ("交运", "换运", "交脱大运")),
    ("dayun:suiyun_note", "suiyun_note", ("岁运并看", "运吉岁凶", "太岁一至")),
)


def _find_quote(raw: str, keywords: tuple[str, ...]) -> str:
    for kw in keywords:
        idx = raw.find(kw)
        if idx >= 0:
            return raw[max(0, idx - 40) : idx + 360].strip()
    return ""


def extract(source_path: Path) -> list[dict]:
    raw = read_source_text(source_path)
    source_file = source_path.name
    nodes: list[dict] = []
    summaries = {
        "core": "大运如地, 太岁如人. 十年一运, 须先看命局用神喜忌, 再论运支是否得地、运干是否助用.",
        "xingyun_xiji": "行运喜忌: 用神在运中得生扶则顺, 忌神当权则逆. 须与流年联看.",
        "gan_zhi_weight": "大运重地支(行运之地), 天干为表象. 运支冲用神之支多逆, 合用神之支多顺.",
        "start_rule": "起运以节气与顺逆为准, 童限小运可补大运不足. 题干虚龄须换算公历再对大运表.",
        "dayun_change": "交运前后一年常主环境、职业或家庭结构变动. 换运时应结合前后两运喜忌对比.",
        "suiyun_note": "大运与流年并看: 运吉岁凶或运凶岁吉, 以用神得失与冲合轻重权衡.",
    }
    for node_id, category, keywords in DAYUN_SPECS:
        quote = _find_quote(raw, keywords)
        if not quote:
            quote = summaries[category]
        nodes.append(
            make_node(
                node_id=node_id,
                topic="dayun",
                source_file=source_file,
                lookup_key={"category": category},
                summary=summaries[category],
                quote=quote[:500] if quote else summaries[category],
                classic="三命通会",
                chapter="论大运流年",
                edition="万民英",
                rule_type="dayun_rule",
                evidence_role="suiyun_judge",
                authority_tier="S",
            )
        )
    return nodes


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
    print(f"extracted {len(nodes)} dayun nodes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
