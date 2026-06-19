"""P0 local validation: judgement baseline sample + optional contest LLM sample."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = BACKEND_ROOT.parents[1] / "report" / "八字判盘最强方案"
REGRESSION_PATH = REPORT_ROOT / "contest8_val_geju_special_regression.json"


def _pick_sample_ids(regression_path: Path, *, per_label: int) -> list[str]:
    payload = json.loads(regression_path.read_text(encoding="utf-8"))
    question_ids: list[str] = []
    for label in ("wrong_tiaohou", "wrong_liunian"):
        picked = 0
        for row in payload.get("rows") or []:
            if row.get("correct"):
                continue
            tags = row.get("errorLabels") or []
            if label not in tags:
                continue
            qid = str(row.get("questionId") or "")
            if not qid or qid in question_ids:
                continue
            question_ids.append(qid)
            picked += 1
            if picked >= per_label:
                break
    return question_ids


def _run_py(script: str, args: list[str]) -> int:
    cmd = [sys.executable, str(BACKEND_ROOT / "scripts" / script), *args]
    print(">", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=str(BACKEND_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regression", type=Path, default=REGRESSION_PATH)
    parser.add_argument("--per-label", type=int, default=4)
    parser.add_argument("--with-llm", action="store_true")
    parser.add_argument("--rag", action="store_true")
    args = parser.parse_args()

    if not args.regression.exists():
        print(f"missing regression: {args.regression}")
        return 1

    question_ids = _pick_sample_ids(args.regression, per_label=args.per_label)
    if not question_ids:
        print("no sample question ids selected")
        return 1

    ids_arg = ",".join(question_ids)
    print("sampleIds:", ids_arg, flush=True)

    suffix = "rag" if args.rag else "local"
    baseline_out = REPORT_ROOT / f"val_judgement_p0_sample_{suffix}.json"
    baseline_args = [
        "--split",
        "val",
        "--ids",
        ids_arg,
        "--output",
        str(baseline_out),
    ]
    if args.rag:
        baseline_args.append("--rag")
    code = _run_py("val_judgement_baseline_local.py", baseline_args)
    if code != 0:
        return code

    summary = json.loads(baseline_out.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "baseline": str(baseline_out),
                "total": summary.get("total"),
                "coverageRate": summary.get("coverageRate"),
                "eventLiunianRate": summary.get("eventLiunianRate"),
                "caseOverreach": summary.get("caseOverreach"),
                "primaryEvidenceMin": summary.get("primaryEvidenceMin"),
                "primaryEvidenceMax": summary.get("primaryEvidenceMax"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    if args.with_llm:
        contest_out = REPORT_ROOT / f"contest8_val_p0_sample_{suffix}.json"
        contest_code = _run_py(
            "run_contest_benchmark.py",
            [
                "--split",
                "val",
                "--ids",
                ids_arg,
                "--out",
                str(contest_out),
            ],
        )
        if contest_code != 0:
            return contest_code
        contest = json.loads(contest_out.read_text(encoding="utf-8"))
        print(
            json.dumps(
                {
                    "contest": str(contest_out),
                    "accuracy": contest.get("accuracy"),
                    "correct": contest.get("correct"),
                    "total": contest.get("total"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
