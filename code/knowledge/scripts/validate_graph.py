"""Validate knowledge nodes and safeAutoAnswer rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
DEFAULT_GRAPH = KNOWLEDGE_DIR / "data" / "graph" / "nodes.jsonl"


def read_source_text(path: Path) -> str:
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def normalize_for_match(text: str) -> str:
    return re.sub(r"\s+", "", text)


def quote_in_source(quote: str, source_text: str) -> bool:
    if not quote:
        return False
    if quote in source_text:
        return True
    return normalize_for_match(quote) in normalize_for_match(source_text)


def load_nodes(path: Path) -> list[dict]:
    nodes: list[dict] = []
    if not path.exists():
        return nodes
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        nodes.append(json.loads(line))
    return nodes


def validate_node(node: dict, source_root: Path) -> list[str]:
    errors: list[str] = []
    node_id = node.get("id", "?")
    tier = node.get("sourceTier", "")
    topic = node.get("topic", "")
    safe = bool(node.get("safeAutoAnswer"))
    claims = node.get("claims") or []
    agreement = node.get("agreementLevel", "")
    domain = node.get("domain", "bazi")

    if not claims:
        errors.append(f"{node_id}: claims empty")
        return errors

    roles = [c.get("role") for c in claims]
    if safe and tier not in ("T1", "T2"):
        errors.append(f"{node_id}: safeAutoAnswer requires T1/T2")
    if safe and topic == "case":
        errors.append(f"{node_id}: case topic cannot be safeAutoAnswer")
    if safe and "contradiction" in roles:
        errors.append(f"{node_id}: contradiction blocks safeAutoAnswer")
    if safe and domain == "bazi-adjacent":
        errors.append(f"{node_id}: bazi-adjacent cannot be safeAutoAnswer in MVP")
    if agreement == "disputed" and safe:
        errors.append(f"{node_id}: disputed cannot be safeAutoAnswer")

    primary = [c for c in claims if c.get("role") == "primary"]
    if safe and not primary:
        errors.append(f"{node_id}: safeAutoAnswer requires primary claim")

    for idx, claim in enumerate(claims):
        quote = claim.get("quote") or ""
        if tier in ("T1", "T2") and not quote:
            errors.append(f"{node_id}: claim {idx} missing quote")
            continue
        source_file = claim.get("sourceFile") or node.get("sourceFile") or ""
        source_category = claim.get("sourceCategory") or node.get("sourceCategory") or ""
        if not source_file:
            continue
        src = source_root / source_category / source_file.replace("\\", "/")
        if not src.exists():
            errors.append(f"{node_id}: source missing {src}")
            continue
        if quote and not quote_in_source(quote, read_source_text(src)):
            errors.append(f"{node_id}: quote not substring of {source_file}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default=str(DEFAULT_GRAPH))
    parser.add_argument("--source-root", default=str(ROOT / "数据库"))
    args = parser.parse_args()
    graph = Path(args.graph)
    source_root = Path(args.source_root)
    nodes = load_nodes(graph)
    if not nodes:
        print("no nodes to validate")
        return 0

    all_errors: list[str] = []
    ids: set[str] = set()
    for node in nodes:
        node_id = node.get("id")
        if node_id in ids:
            all_errors.append(f"duplicate id: {node_id}")
        ids.add(node_id)
        all_errors.extend(validate_node(node, source_root))

    if all_errors:
        print("\n".join(all_errors))
        return 1
    print(f"validated {len(nodes)} nodes ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
