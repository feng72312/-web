"""Set reviewedAt and optional reviewerNotes on knowledge graph nodes."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
DRAFT_DIR = KNOWLEDGE_DIR / "data" / "draft"
GRAPH_PATH = KNOWLEDGE_DIR / "data" / "graph" / "nodes.jsonl"


def _patch_file(path: Path, ids: set[str], reviewed_at: str, notes: str) -> int:
    if not path.exists():
        return 0
    rows: list[str] = []
    changed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        node = json.loads(line)
        if node.get("id") in ids:
            node["reviewedAt"] = reviewed_at
            if notes:
                node["reviewerNotes"] = notes
            changed += 1
        rows.append(json.dumps(node, ensure_ascii=False))
    if changed:
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", required=True, help="comma-separated node ids")
    parser.add_argument("--notes", default="")
    parser.add_argument("--timestamp", default="")
    args = parser.parse_args()

    ids = {item.strip() for item in args.ids.split(",") if item.strip()}
    if not ids:
        print("no ids provided")
        return 1

    reviewed_at = args.timestamp or datetime.now().isoformat(timespec="seconds")
    total = 0
    for path in sorted(DRAFT_DIR.glob("*.jsonl")):
        total += _patch_file(path, ids, reviewed_at, args.notes)
    total += _patch_file(GRAPH_PATH, ids, reviewed_at, args.notes)
    print(f"marked={total} reviewedAt={reviewed_at}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
