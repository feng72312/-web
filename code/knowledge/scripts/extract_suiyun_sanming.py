"""Extract suiyun/dayun nodes from 三命通会 into draft JSONL."""

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
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "suiyun_sanming.draft.jsonl"

GANS = list("甲乙丙丁戊己庚辛壬癸")
ZHIS = list("子丑寅卯辰巳午未申酉戌亥")
GANZHI_RE = re.compile(r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])")

SECTION_KEYS = {
    "大运": "dayun_core",
    "流年": "liunian_core",
    "岁运": "suiyun_core",
    "行运": "xingyun",
    "太岁": "taisui",
}


def extract(source_path: Path) -> list[dict]:
    raw = read_source_text(source_path)
    source_file = source_path.name
    nodes: list[dict] = []
    seen_gz: set[str] = set()

    for keyword, category in SECTION_KEYS.items():
        for match in re.finditer(rf"《[^》]*{keyword}[^》]*》|论{keyword}|{keyword}", raw):
            start = match.start()
            quote = raw[start : start + 400].strip()
            if len(quote) < 40:
                continue
            node_id = f"suiyun:category:{category}"
            if node_id in {n["id"] for n in nodes}:
                continue
            nodes.append(
                make_node(
                    node_id=node_id,
                    topic="suiyun",
                    source_file=source_file,
                    lookup_key={"category": category},
                    summary=trim_summary(quote, 100),
                    quote=quote,
                    classic="三命通会",
                    chapter=keyword,
                    edition="万民英",
                    rule_type="suiyun_rule",
                    evidence_role="suiyun_judge",
                )
            )

    for gz in GANZHI_RE.findall(raw):
        if gz in seen_gz:
            continue
        seen_gz.add(gz)
        if len(seen_gz) > 60:
            break
        idx = raw.find(gz)
        quote = raw[idx : idx + 300].strip()
        if len(quote) < 30:
            continue
        node_id = f"suiyun:ganzhi:{gz}"
        nodes.append(
            make_node(
                node_id=node_id,
                topic="suiyun",
                source_file=source_file,
                lookup_key={"ganzhi": gz, "category": "ganzhi_dayun"},
                summary=trim_summary(quote, 100),
                quote=quote,
                classic="三命通会",
                chapter=f"大运流年 {gz}",
                edition="万民英",
                rule_type="suiyun_ganzhi",
                evidence_role="suiyun_judge",
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
    print(f"extracted {len(nodes)} suiyun nodes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
