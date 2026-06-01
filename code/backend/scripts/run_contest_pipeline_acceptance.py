#!/usr/bin/env python
"""P1/P2 acceptance runs for contest MCQ pipeline upgrade."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT.parents[1] / "report"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import importlib.util

from app.benchmark.contest8_eval import run_eval, save_report

_liunian_path = ROOT / "scripts" / "run_contest_liunian_eval.py"
_spec = importlib.util.spec_from_file_location("run_contest_liunian_eval", _liunian_path)
_liunian_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_liunian_mod)
filter_questions = _liunian_mod.filter_questions
run_liunian_eval = _liunian_mod.run_eval


P1_MIN = 10
P2_MIN = 13


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--votes", type=int, default=3)
    parser.add_argument("--skip-val", action="store_true")
    args = parser.parse_args()

    lines = [
        "# Contest pipeline acceptance",
        "",
        f"- time: {datetime.now().isoformat(timespec='seconds')}",
        f"- model: {args.model or 'deepseek-chat'}",
        f"- votes: {args.votes}",
        "",
    ]

    p1 = asyncio.run(
        run_liunian_eval(
            filter_questions("strict"),
            args.model,
            votes=args.votes,
        )
    )
    p1_ok = p1["correct"] >= P1_MIN
    lines.append(f"## P1 strict 19: {p1['correct']}/{p1['total']} = {p1['accuracy']:.1%}")
    lines.append(f"- pass (>={P1_MIN}): **{p1_ok}**")
    lines.append("")

    p2_ok = False
    if not args.skip_val:
        report = asyncio.run(
            run_eval(
                "val",
                model_id=args.model,
                use_knowledge=True,
                use_case_rag=True,
                use_fewshot=True,
                votes=args.votes,
                temperature=0.2,
                theme_fewshot=True,
            )
        )
        out = ROOT / "data" / "reports" / "contest8_val_pipeline_p2.json"
        save_report(report, out)
        p2_ok = report.correct >= P2_MIN
        lines.append(
            f"## P2 val 40: {report.correct}/{report.total} = {report.accuracy:.1%}"
        )
        lines.append(f"- pass (>={P2_MIN}): **{p2_ok}**")
        lines.append(f"- json: {out}")
        lines.append("")

    out_md = REPORT_DIR / "命理师大赛-管线升级验收.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"wrote {out_md}")

    if not p1_ok:
        sys.exit(1)
    if not args.skip_val and not p2_ok:
        sys.exit(2)


if __name__ == "__main__":
    main()
