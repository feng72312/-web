"""Audit a sample of case records for structureTags/eventYear/observedEvent quality."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.knowledge.case_match import (  # noqa: E402
    case_has_readable_body,
    is_applicable_case,
    is_catalog_case,
    readable_verdict_excerpt,
)

CASES_PATH = BACKEND_ROOT.parents[0] / "knowledge" / "data" / "cases" / "cases.jsonl"


def audit_row(row: dict) -> dict:
    verdict = str(row.get("verdict") or "")
    return {
        "id": row.get("id"),
        "sourceFile": row.get("sourceFile"),
        "applicable": is_applicable_case(row),
        "catalogLike": is_catalog_case(row),
        "readableBody": case_has_readable_body(row),
        "structureTags": row.get("structureTags") or [],
        "eventTags": row.get("eventTags") or [],
        "eventYear": row.get("eventYear") or [],
        "observedEvent": row.get("observedEvent") or "",
        "chartPattern": row.get("chartPattern") or "",
        "doNotApplyReason": row.get("doNotApplyReason") or "",
        "excerptPreview": readable_verdict_excerpt(verdict, limit=120),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=10)
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    rows = [json.loads(line) for line in CASES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    step = max(len(rows) // max(args.sample, 1), 1)
    picked = [rows[idx] for idx in range(0, len(rows), step)][: args.sample]
    audits = [audit_row(row) for row in picked]
    payload = {
        "totalCases": len(rows),
        "sampleSize": len(audits),
        "applicableInSample": sum(1 for row in audits if row["applicable"]),
        "readableInSample": sum(1 for row in audits if row["readableBody"]),
        "rows": audits,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
