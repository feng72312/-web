#!/usr/bin/env python
"""Run Contest8 with Bazi+Ziwei fusion (rule merge, optional arbitrate)."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT.parents[1] / "report"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import split_summary
from app.benchmark.contest8_eval import run_eval, save_report

SPLITS = ("train", "val", "test")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("train", "val", "test", "all"), default="val")
    parser.add_argument("--arbitrate", action="store_true", help="Plan B: LLM on disagree")
    parser.add_argument("--votes", type=int, default=1)
    args = parser.parse_args()

    tag = "bazi_ziwei_arb" if args.arbitrate else "bazi_ziwei"
    print("dataset:", split_summary())
    print(f"mode: bazi+ziwei fusion tag={tag} votes={args.votes}")

    splits = SPLITS if args.split == "all" else (args.split,)
    totals = []
    for name in splits:
        report = await run_eval(
            name,  # type: ignore[arg-type]
            use_knowledge=True,
            use_case_rag=True,
            use_fewshot=True,
            use_bazi_ziwei_fusion=True,
            fusion_arbitrate=args.arbitrate,
            votes=args.votes,
            temperature=0.2,
            theme_fewshot=True,
        )
        out = ROOT / "data" / "reports" / f"contest8_{name}_{tag}.json"
        save_report(report, out)
        totals.append(report)
        print(f"[{name}] {report.correct}/{report.total} = {report.accuracy:.1%} -> {out}")

    if len(totals) > 1:
        c = sum(r.correct for r in totals)
        t = sum(r.total for r in totals)
        lines = [
            f"# Contest8 Bazi+Ziwei ({tag})",
            "",
            f"Total: **{c}/{t} = {c/t:.1%}**",
            "",
            "| split | acc |",
            "|-------|-----|",
        ]
        for r in totals:
            lines.append(f"| {r.split} | {r.correct}/{r.total} ({r.accuracy:.1%}) |")
        md = REPORT_DIR / f"命理师大赛-全量200题-{tag}.md"
        md.write_text("\n".join(lines), encoding="utf-8")
        print(f"total {c}/{t} -> {md}")


if __name__ == "__main__":
    asyncio.run(main())
