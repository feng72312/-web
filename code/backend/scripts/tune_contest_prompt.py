#!/usr/bin/env python
"""
Tune contest MCQ setup on val (2024) after building few-shot from train.

1. Build few-shot from train (2021-2023)
2. Eval val without few-shot
3. Eval val with few-shot
4. Write comparison report
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_eval import run_eval, save_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--fewshot-count", type=int, default=8)
    args = parser.parse_args()

    fewshot_script = ROOT / "scripts" / "build_contest_fewshot.py"
    subprocess.run(
        [sys.executable, str(fewshot_script), "--count", str(args.fewshot_count)],
        check=True,
    )

    reports_dir = ROOT / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    baseline = asyncio.run(
        run_eval(
            "val",
            model_id=args.model,
            limit=args.limit,
            use_fewshot=False,
        )
    )
    tuned = asyncio.run(
        run_eval(
            "val",
            model_id=args.model,
            limit=args.limit,
            use_fewshot=True,
        )
    )

    save_report(baseline, reports_dir / "contest8_val_baseline.json")
    save_report(tuned, reports_dir / "contest8_val_fewshot.json")

    comparison = {
        "val_baseline_accuracy": baseline.accuracy,
        "val_fewshot_accuracy": tuned.accuracy,
        "delta": tuned.accuracy - baseline.accuracy,
        "fewshot_count": args.fewshot_count,
    }
    comp_path = reports_dir / "contest8_tune_comparison.json"
    comp_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"baseline val: {baseline.accuracy:.1%} ({baseline.correct}/{baseline.total})")
    print(f"fewshot val:  {tuned.accuracy:.1%} ({tuned.correct}/{tuned.total})")
    print(f"delta:        {comparison['delta']:+.1%}")
    print(f"comparison -> {comp_path}")


if __name__ == "__main__":
    main()
