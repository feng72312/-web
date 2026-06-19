"""Local judgement regression gate: val baseline + optional LLM sample."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = BACKEND_ROOT.parents[1] / "report" / "八字判盘最强方案"
CONTINUE_ROOT = REPORT_ROOT / "继续补全"
REGRESSION_PATH = REPORT_ROOT / "contest8_val_geju_special_regression.json"
P0_SAMPLE_IDS = (
    "guangdong_female_19800824_P001-Q1,"
    "guangdong_female_19800824_P001-Q2,"
    "guangdong_female_19800824_P001-Q3,"
    "guangdong_female_19800824_P001-Q4,"
    "guangdong_female_19800824_P001-Q5,"
    "male_19611230_P003-Q13,"
    "female_19831028_P004-Q17,"
    "female_19831028_P004-Q19"
)


def _run_py(script: str, args: list[str]) -> tuple[int, str]:
    cmd = [sys.executable, str(BACKEND_ROOT / "scripts" / script), *args]
    print(">", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=str(BACKEND_ROOT), capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout, end="", flush=True)
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr, flush=True)
    return proc.returncode, proc.stdout


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _check_gate(
    summary: dict,
    *,
    min_coverage: float,
    max_case_overreach: int,
) -> list[str]:
    failures: list[str] = []
    coverage = float(summary.get("coverageRate") or 0.0)
    overreach = int(summary.get("caseOverreach") or 0)
    if coverage < min_coverage:
        failures.append(f"coverageRate {coverage:.3f} < {min_coverage:.3f}")
    if overreach > max_case_overreach:
        failures.append(f"caseOverreach {overreach} > {max_case_overreach}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--rag", action="store_true", default=True)
    parser.add_argument("--no-rag", action="store_true")
    parser.add_argument("--with-llm", action="store_true")
    parser.add_argument("--min-coverage", type=float, default=0.95)
    parser.add_argument("--max-case-overreach", type=int, default=1)
    parser.add_argument("--min-llm-accuracy", type=float, default=0.125)
    parser.add_argument("--check-authority-audit", action="store_true")
    parser.add_argument("--with-wrong-sample", action="store_true")
    parser.add_argument("--max-wrong-sample-labels", type=int, default=999)
    parser.add_argument(
        "--output",
        type=Path,
        default=CONTINUE_ROOT / "regression_gate_baseline.json",
    )
    args = parser.parse_args()
    use_rag = not args.no_rag

    CONTINUE_ROOT.mkdir(parents=True, exist_ok=True)
    suffix = "rag" if use_rag else "local"
    val_out = CONTINUE_ROOT / f"regression_gate_val_{args.limit}_{suffix}.json"

    val_args = [
        "--split",
        "val",
        "--limit",
        str(args.limit),
        "--output",
        str(val_out),
    ]
    if use_rag:
        val_args.append("--rag")
    code, _ = _run_py("val_judgement_baseline_local.py", val_args)
    if code != 0:
        return code

    val_summary = _load_json(val_out)
    failures = _check_gate(
        val_summary,
        min_coverage=args.min_coverage,
        max_case_overreach=args.max_case_overreach,
    )

    p0_out = CONTINUE_ROOT / f"regression_gate_p0_{suffix}.json"
    p0_args = [
        "--split",
        "val",
        "--ids",
        P0_SAMPLE_IDS,
        "--output",
        str(p0_out),
    ]
    if use_rag:
        p0_args.append("--rag")
    code, _ = _run_py("val_judgement_baseline_local.py", p0_args)
    if code != 0:
        return code
    p0_summary = _load_json(p0_out)
    failures.extend(
        _check_gate(
            p0_summary,
            min_coverage=1.0,
            max_case_overreach=0,
        )
    )

    llm_summary: dict | None = None
    if args.with_llm:
        contest_out = CONTINUE_ROOT / f"regression_gate_contest8_{suffix}.json"
        contest_args = [
            "--split",
            "val",
            "--ids",
            P0_SAMPLE_IDS,
            "--out",
            str(contest_out),
        ]
        code, _ = _run_py("run_contest_benchmark.py", contest_args)
        if code != 0:
            return code
        llm_summary = _load_json(contest_out)
        accuracy = float(llm_summary.get("accuracy") or 0.0)
        if accuracy < args.min_llm_accuracy:
            failures.append(
                f"llm accuracy {accuracy:.3f} < {args.min_llm_accuracy:.3f}"
            )

    if args.check_authority_audit:
        audit_path = CONTINUE_ROOT / "node_authority_audit.json"
        audit_script = BACKEND_ROOT.parent / "knowledge" / "scripts" / "audit_node_authority.py"
        cmd = [sys.executable, str(audit_script), "--output", str(audit_path)]
        print(">", " ".join(cmd), flush=True)
        proc = subprocess.run(cmd, cwd=str(audit_script.parent), capture_output=True, text=True)
        if proc.stdout:
            print(proc.stdout, end="", flush=True)
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr, flush=True)
        if audit_path.is_file():
            audit = _load_json(audit_path)
            primary_bad = int(audit.get("primaryJudgeMismatchCount") or 0)
            if primary_bad > 0:
                failures.append(f"authority audit primary mismatches={primary_bad}")
        elif proc.returncode != 0:
            failures.append("authority audit failed")

    wrong_sample_summary: dict | None = None
    if args.with_wrong_sample:
        wrong_out = CONTINUE_ROOT / f"regression_gate_wrong_sample_{suffix}.json"
        wrong_args = ["--limit", "10", "--out", str(wrong_out)]
        code, _ = _run_py("run_contest_wrong_tiaohou_liunian_sample.py", wrong_args)
        if code != 0:
            return code
        wrong_sample_summary = _load_json(wrong_out)
        label_total = 0
        for row in wrong_sample_summary.get("results") or []:
            labels = set(row.get("errorLabels") or [])
            if labels.intersection({"overconfident_claim", "wrong_tiaohou", "wrong_liunian"}):
                label_total += 1
        if label_total > args.max_wrong_sample_labels:
            failures.append(
                f"wrong sample focus labels {label_total} > {args.max_wrong_sample_labels}"
            )

    payload = {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "useRag": use_rag,
        "thresholds": {
            "minCoverage": args.min_coverage,
            "maxCaseOverreach": args.max_case_overreach,
            "minLlmAccuracy": args.min_llm_accuracy if args.with_llm else None,
        },
        "valBaseline": {
            "path": str(val_out),
            "total": val_summary.get("total"),
            "coverageRate": val_summary.get("coverageRate"),
            "eventLiunianRate": val_summary.get("eventLiunianRate"),
            "caseOverreach": val_summary.get("caseOverreach"),
            "primaryEvidenceMin": val_summary.get("primaryEvidenceMin"),
            "primaryEvidenceMax": val_summary.get("primaryEvidenceMax"),
        },
        "p0Baseline": {
            "path": str(p0_out),
            "total": p0_summary.get("total"),
            "coverageRate": p0_summary.get("coverageRate"),
            "eventLiunianRate": p0_summary.get("eventLiunianRate"),
            "caseOverreach": p0_summary.get("caseOverreach"),
            "primaryEvidenceMin": p0_summary.get("primaryEvidenceMin"),
            "primaryEvidenceMax": p0_summary.get("primaryEvidenceMax"),
        },
        "llmSample": None,
        "wrongSample": wrong_sample_summary,
        "passed": not failures,
        "failures": failures,
    }
    if llm_summary:
        payload["llmSample"] = {
            "path": str(contest_out),
            "accuracy": llm_summary.get("accuracy"),
            "correct": llm_summary.get("correct"),
            "total": llm_summary.get("total"),
        }

    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if failures:
        print("GATE FAILED:", "; ".join(failures), file=sys.stderr)
        return 1
    print("GATE PASSED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
