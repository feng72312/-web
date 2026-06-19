"""Audit graph node authority against bazi_sources_manifest."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
GRAPH_PATH = KNOWLEDGE_DIR / "data" / "graph" / "nodes.jsonl"
MANIFEST_PATH = KNOWLEDGE_DIR / "data" / "sources" / "bazi_sources_manifest.json"
DEFAULT_OUTPUT = (
    KNOWLEDGE_DIR.parents[1]
    / "report"
    / "八字判盘最强方案"
    / "继续补全"
    / "node_authority_audit.json"
)

PRIMARY_ROLES = {
    "tiaohou_judge",
    "geju_judge",
    "qishi_judge",
    "shishen_judge",
    "suiyun_judge",
    "primary_judge",
}


def _load_manifest(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tier_by_file: dict[str, str] = {}
    for row in data.get("files") or []:
        if not isinstance(row, dict):
            continue
        fname = str(row.get("sourceFile") or row.get("fileName") or "")
        tier = str(row.get("authorityTier") or row.get("tier") or "")
        if not fname or not tier:
            continue
        tier_by_file[fname] = tier
        tier_by_file[Path(fname).name] = tier
        base = Path(fname).name
        if "/" in fname or "\\" in fname:
            tier_by_file[base] = tier
    return tier_by_file


def _load_nodes() -> list[dict]:
    rows: list[dict] = []
    for line in GRAPH_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def audit() -> dict:
    tier_by_file = _load_manifest(MANIFEST_PATH)
    mismatches: list[dict] = []
    for node in _load_nodes():
        source_file = str(node.get("sourceFile") or "")
        evidence_role = str(node.get("evidenceRole") or "")
        node_tier = str(node.get("authorityTier") or "S")
        manifest_tier = tier_by_file.get(source_file) or tier_by_file.get(Path(source_file).name) or ""
        is_primary = evidence_role in PRIMARY_ROLES or node.get("topic") in (
            "tiaohou",
            "geju",
            "qishi",
            "shishen",
            "suiyun",
            "dayun",
        )
        issue = ""
        if manifest_tier in ("B", "D") and is_primary:
            issue = "primary_judge_from_low_tier_source"
        elif manifest_tier and manifest_tier != node_tier and manifest_tier in ("S", "A"):
            issue = "node_tier_differs_from_manifest"
        if issue:
            mismatches.append(
                {
                    "id": node.get("id"),
                    "topic": node.get("topic"),
                    "sourceFile": source_file,
                    "manifestTier": manifest_tier,
                    "nodeTier": node_tier,
                    "evidenceRole": evidence_role,
                    "issue": issue,
                }
            )
    return {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "nodeCount": len(_load_nodes()),
        "mismatchCount": len(mismatches),
        "primaryJudgeMismatchCount": sum(
            1 for m in mismatches if m.get("issue") == "primary_judge_from_low_tier_source"
        ),
        "mismatches": mismatches,
        "passed": len(mismatches) == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {args.output} mismatches={payload['mismatchCount']}")
    if payload["primaryJudgeMismatchCount"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
