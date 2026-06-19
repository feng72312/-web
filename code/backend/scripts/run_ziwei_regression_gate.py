"""Ziwei judgement + contest ziwei-only regression gate."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = BACKEND_ROOT.parents[1] / "report" / "紫薇斗数最强方案"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.benchmark.contest8_dataset import SplitName, load_split
from app.benchmark.contest8_ziwei_chart import build_ziwei_chart_for_question
from app.benchmark.ziwei_error_labels import aggregate_ziwei_error_label_counts
from app.core.ziwei.judgement.chain import ZiweiJudgementChain

DEFAULT_SMOKE_LIMIT = 5


def _run_py(script: str, args: list[str]) -> int:
    cmd = [sys.executable, str(BACKEND_ROOT / "scripts" / script), *args]
    print(">", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=str(BACKEND_ROOT))
    return int(proc.returncode or 0)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _check_rag_health(url: str = "http://127.0.0.1:8100/health") -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


async def run_offline_coverage(
    *,
    split: SplitName,
    limit: int,
    question_ids: list[str] | None,
    use_rag: bool,
) -> dict:
    questions = load_split(split)
    if question_ids:
        id_set = set(question_ids)
        questions = [q for q in questions if q.question_id in id_set]
    else:
        questions = questions[:limit]

    chain = ZiweiJudgementChain(use_rag=use_rag)
    rows: list[dict] = []
    covered = 0

    for q in questions:
        chart = build_ziwei_chart_for_question(q)
        report = await chain.run(
            chart,
            question=q.question,
            target_year=q.year,
        )
        payload = report.to_dict()
        enriched = payload.get("enrichedChart") or {}
        judge_count = len(payload.get("judges") or [])
        step_count = len(payload.get("steps") or [])
        roles = {row.get("role") for row in payload.get("judges") or []}
        required = {
            "topic",
            "palace",
            "star",
            "mutagen",
            "pattern",
            "limit",
            "cross_school",
        }
        ok = (
            judge_count >= 7
            and step_count >= 7
            and required.issubset(roles)
            and bool(enriched.get("palaces"))
        )
        if ok:
            covered += 1
        rows.append(
            {
                "questionId": q.question_id,
                "topicId": (payload.get("topic") or {}).get("topicId"),
                "judgeCount": judge_count,
                "stepCount": step_count,
                "judgeRoles": sorted(roles),
                "confidenceBand": (payload.get("arbitration") or {}).get("confidenceBand"),
                "covered": ok,
            }
        )

    total = len(rows)
    return {
        "split": split,
        "total": total,
        "covered": covered,
        "coverageRate": round(covered / total, 4) if total else 0.0,
        "useRag": use_rag,
        "results": rows,
    }


def _check_offline_gate(summary: dict, *, min_coverage: float) -> list[str]:
    failures: list[str] = []
    rate = float(summary.get("coverageRate") or 0.0)
    if rate < min_coverage:
        failures.append(f"coverageRate {rate:.3f} < {min_coverage:.3f}")
    return failures


def _check_smoke_gate(contest_report: dict, *, min_nonempty: float) -> list[str]:
    failures: list[str] = []
    results = contest_report.get("results") or []
    if not results:
        failures.append("smoke results empty")
        return failures
    nonempty = sum(
        1
        for row in results
        if str(row.get("ziweiPred") or row.get("predicted") or "")
    )
    rate = nonempty / len(results)
    if rate < min_nonempty:
        failures.append(f"nonemptyPredRate {rate:.3f} < {min_nonempty:.3f}")
    missing_labels = [
        row.get("question_id") or row.get("questionId")
        for row in results
        if "errorLabels" not in row
    ]
    if missing_labels:
        failures.append(f"missing errorLabels on {len(missing_labels)} rows")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("train", "val", "test"), default="val")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--ids", default="", help="comma-separated question ids")
    parser.add_argument("--offline-only", action="store_true")
    parser.add_argument("--smoke", action="store_true", help="run ziwei-only contest smoke")
    parser.add_argument("--rag", action="store_true", default=True)
    parser.add_argument("--no-rag", action="store_true")
    parser.add_argument("--skip-rag-health", action="store_true")
    parser.add_argument("--min-coverage", type=float, default=0.95)
    parser.add_argument("--min-nonempty-pred", type=float, default=1.0)
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPORT_ROOT / "contest8_ziwei_smoke.json",
    )
    args = parser.parse_args()

    use_rag = not args.no_rag
    question_ids = [item.strip() for item in args.ids.split(",") if item.strip()] or None
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    rag_health = None
    if use_rag and not args.skip_rag_health:
        rag_health = _check_rag_health()
        if not rag_health:
            failures.append("rag health check failed (8100)")

    offline_limit = args.limit if not args.smoke else max(args.limit, DEFAULT_SMOKE_LIMIT)
    offline_summary = asyncio.run(
        run_offline_coverage(
            split=args.split,
            limit=offline_limit,
            question_ids=question_ids,
            use_rag=use_rag,
        )
    )
    offline_path = REPORT_ROOT / f"ziwei_offline_coverage_{args.split}_{offline_limit}.json"
    offline_path.write_text(
        json.dumps(offline_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    failures.extend(_check_offline_gate(offline_summary, min_coverage=args.min_coverage))

    contest_summary: dict | None = None
    if args.smoke and not args.offline_only:
        smoke_limit = DEFAULT_SMOKE_LIMIT if not question_ids else len(question_ids)
        contest_out = args.output
        contest_args = [
            "--split",
            args.split,
            "--ziwei-only",
            "--limit",
            str(smoke_limit),
            "--out",
            str(contest_out),
        ]
        if question_ids:
            contest_args.extend(["--ids", ",".join(question_ids)])
        if args.model:
            contest_args.extend(["--model", args.model])
        code = _run_py("run_contest_benchmark.py", contest_args)
        if code != 0:
            failures.append(f"run_contest_benchmark exited {code}")
        elif contest_out.is_file():
            contest_summary = _load_json(contest_out)
            failures.extend(
                _check_smoke_gate(contest_summary, min_nonempty=args.min_nonempty_pred)
            )

    error_label_counts = (
        aggregate_ziwei_error_label_counts(contest_summary.get("results") or [])
        if contest_summary
        else {}
    )

    payload = {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "split": args.split,
        "useRag": use_rag,
        "ragHealth": rag_health,
        "offlineCoverage": {
            "path": str(offline_path),
            **{k: offline_summary.get(k) for k in ("total", "covered", "coverageRate")},
        },
        "smokeContest": None,
        "errorLabelCounts": error_label_counts,
        "thresholds": {
            "minCoverage": args.min_coverage,
            "minNonemptyPred": args.min_nonempty_pred,
        },
        "passed": not failures,
        "failures": failures,
    }
    if contest_summary:
        payload["smokeContest"] = {
            "path": str(args.output),
            "total": contest_summary.get("total"),
            "correct": contest_summary.get("correct"),
            "accuracy": contest_summary.get("accuracy"),
            "nonemptyPred": sum(
                1
                for row in contest_summary.get("results") or []
                if str(row.get("ziweiPred") or row.get("predicted") or "")
            ),
        }

    gate_path = REPORT_ROOT / "ziwei_regression_gate.json"
    gate_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if failures:
        print("GATE FAILED:", "; ".join(failures), file=sys.stderr)
        return 1
    print("GATE PASSED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
