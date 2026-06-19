"""Generate val-split regression report for contest benchmark."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from app.benchmark.contest8_benchmark_meta import check_judgement_coverage, enrich_question
from app.benchmark.contest8_dataset import load_split


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="val")
    parser.add_argument("--results", required=True, help="JSON eval report from contest8_eval")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    results_path = Path(args.results)
    if not results_path.exists():
        print(f"missing results: {results_path}")
        return 1
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    by_id = {row["question_id"]: row for row in payload.get("results", [])}
    questions = load_split(args.split)  # type: ignore[arg-type]

    label_counter: Counter[str] = Counter()
    coverage_ok = 0
    rows: list[dict] = []
    for item in questions:
        meta = enrich_question(item)
        result = by_id.get(item.question_id, {})
        judgement = result.get("judgement") or {}
        coverage = check_judgement_coverage(judgement, meta)
        if coverage.get("covered"):
            coverage_ok += 1
        for label in result.get("errorLabels") or []:
            label_counter[label] += 1
        rows.append(
            {
                "questionId": item.question_id,
                "correct": result.get("correct", False),
                "meta": meta,
                "coverage": coverage,
                "errorLabels": result.get("errorLabels") or [],
            }
        )

    report = {
        "split": args.split,
        "total": len(questions),
        "accuracy": payload.get("accuracy", 0.0),
        "coverageOk": coverage_ok,
        "errorLabelDistribution": dict(label_counter),
        "rows": rows,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
