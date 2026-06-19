"""Batch mark reviewedAt on high-frequency graph nodes by topic."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
GRAPH_PATH = KNOWLEDGE_DIR / "data" / "graph" / "nodes.jsonl"
MARK_SCRIPT = KNOWLEDGE_DIR / "scripts" / "mark_node_reviewed.py"

DEFAULT_LIMITS = {
    "tiaohou": 30,
    "geju": 20,
    "liunian": 15,
    "interactions": 15,
    "shishen": 10,
    "qishi": 10,
}


def _load_nodes() -> list[dict]:
    rows: list[dict] = []
    if not GRAPH_PATH.exists():
        return rows
    for line in GRAPH_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _pick_ids(nodes: list[dict], limits: dict[str, int]) -> list[str]:
    by_topic: dict[str, list[dict]] = {}
    for node in nodes:
        topic = str(node.get("topic") or "")
        by_topic.setdefault(topic, []).append(node)
    picked: list[str] = []
    for topic, limit in limits.items():
        for node in by_topic.get(topic, [])[:limit]:
            nid = str(node.get("id") or "")
            if nid:
                picked.append(nid)
    return picked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notes", default="batch review phase J")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    nodes = _load_nodes()
    ids = _pick_ids(nodes, DEFAULT_LIMITS)
    if not ids:
        print("no nodes to review")
        return 1
    print(f"selected {len(ids)} nodes across topics")
    if args.dry_run:
        print(",".join(ids[:20]), "...")
        return 0

    cmd = [
        sys.executable,
        str(MARK_SCRIPT),
        "--ids",
        ",".join(ids),
        "--notes",
        args.notes,
        "--timestamp",
        datetime.now().isoformat(timespec="seconds"),
    ]
    proc = subprocess.run(cmd, cwd=str(KNOWLEDGE_DIR / "scripts"))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
