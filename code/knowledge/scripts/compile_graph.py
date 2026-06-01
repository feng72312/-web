"""Merge draft node files into graph/nodes.jsonl and update manifest.json."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
DRAFT_DIR = KNOWLEDGE_DIR / "data" / "draft"
GRAPH_PATH = KNOWLEDGE_DIR / "data" / "graph" / "nodes.jsonl"
MANIFEST_PATH = KNOWLEDGE_DIR / "data" / "manifest.json"
INDEX_PATH = KNOWLEDGE_DIR / "data" / "sources" / "01_index.json"
CROSS_PATH = KNOWLEDGE_DIR / "data" / "cross_category_manifest.json"


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_extra_nodes(draft_dir: Path) -> list[dict]:
    nodes: list[dict] = []
    if not draft_dir.exists():
        return nodes
    for path in sorted(draft_dir.glob("*.jsonl")):
        nodes.extend(load_jsonl(path))
    return nodes


def dedupe(nodes: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for node in nodes:
        node_id = node["id"]
        if node_id not in merged:
            merged[node_id] = node
            continue
        if len(node.get("summary", "")) > len(merged[node_id].get("summary", "")):
            merged[node_id] = node
    return list(merged.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", default=str(DRAFT_DIR))
    parser.add_argument("--graph", default=str(GRAPH_PATH))
    args = parser.parse_args()

    nodes = dedupe(load_extra_nodes(Path(args.draft)))
    graph_path = Path(args.graph)
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    with graph_path.open("w", encoding="utf-8") as fh:
        for node in nodes:
            fh.write(json.dumps(node, ensure_ascii=False) + "\n")

    by_tier: dict[str, int] = {}
    by_topic: dict[str, int] = {}
    for node in nodes:
        tier = node.get("sourceTier", "?")
        topic = node.get("topic", "?")
        by_tier[tier] = by_tier.get(tier, 0) + 1
        by_topic[topic] = by_topic.get(topic, 0) + 1

    index_count = 0
    if INDEX_PATH.exists():
        index_count = json.loads(INDEX_PATH.read_text(encoding="utf-8")).get("filesTotal", 0)
    cross_count = 0
    if CROSS_PATH.exists():
        cross_count = len(json.loads(CROSS_PATH.read_text(encoding="utf-8")).get("entries", []))

    manifest = {
        "version": "1.0.0-pilot",
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "nodeCount": len(nodes),
        "byTier": by_tier,
        "byTopic": by_topic,
        "01FilesIndexed": index_count,
        "crossCategoryCount": cross_count,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
