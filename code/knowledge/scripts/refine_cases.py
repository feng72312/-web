"""Refine extracted case records: catalog filter, observedEvent, verdict excerpt."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.knowledge.case_match import (  # noqa: E402
    is_applicable_case,
    is_catalog_case,
    readable_verdict_excerpt,
)

CASES_PATH = Path(__file__).resolve().parents[1] / "data" / "cases" / "cases.jsonl"
STEM_NOISE = re.compile(r"^(实战命例|自在道人实战命例|实自在道人战命例|函测命例)")


def _clean_observed_event(source_file: str, text: str) -> str:
    stem = Path(source_file).stem
    for token in ("实战命例", "函测命例", "命例", "曲炜", "蔡昔琼", "自在道人"):
        if token in stem:
            stem = stem.split(token, 1)[-1]
    stem = STEM_NOISE.sub("", stem).strip("._- 　")
    if stem and not stem.isdigit() and len(stem) >= 2:
        return stem[:80]
    excerpt = readable_verdict_excerpt(text, limit=80)
    if excerpt:
        return excerpt[:80]
    return stem[:80] if stem else ""


def refine_row(row: dict) -> dict:
    updated = dict(row)
    verdict = str(row.get("verdict") or "")
    source_file = str(row.get("sourceFile") or "")
    updated["observedEvent"] = _clean_observed_event(source_file, verdict) or updated.get("observedEvent", "")
    excerpt = readable_verdict_excerpt(verdict)
    if excerpt:
        updated["verdict"] = excerpt
        updated["confidence"] = "medium"
    reason = str(row.get("doNotApplyReason") or "").strip()
    if not reason and is_catalog_case(updated):
        updated["doNotApplyReason"] = "catalog_or_index"
    elif reason in {"binary_or_unreadable", "read_failed:doc_batch", "text_too_short"}:
        updated["doNotApplyReason"] = reason
    updated["refinedAt"] = datetime.now().isoformat(timespec="seconds")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(CASES_PATH))
    parser.add_argument("--output", default=str(CASES_PATH))
    args = parser.parse_args()
    in_path = Path(args.input)
    if not in_path.exists():
        print(f"missing: {in_path}")
        return 1
    rows = [json.loads(line) for line in in_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    refined = [refine_row(row) for row in rows]
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for row in refined:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    applicable = sum(1 for row in refined if is_applicable_case(row))
    blocked = sum(1 for row in refined if row.get("doNotApplyReason"))
    print(f"refined {len(refined)} cases -> {out_path}")
    print(f"applicable={applicable} blocked={blocked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
