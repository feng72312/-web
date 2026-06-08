#!/usr/bin/env python
"""Run full 200 Contest8 MCQ with Ziwei-only channel."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT.parents[1] / "report"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import split_summary
from app.benchmark.contest8_eval import run_eval, save_report

TAG = "ziwei_only"
SPLITS = ("train", "val", "test")


async def main() -> None:
    print("dataset:", split_summary())
    print("config: Ziwei chart + horoscope + RAG(11紫微斗数) + deepseek-chat")
    reports = {}
    for name in SPLITS:
        report = await run_eval(
            name,  # type: ignore[arg-type]
            use_knowledge=False,
            use_case_rag=True,
            use_fewshot=False,
            use_ziwei_only=True,
        )
        out = ROOT / "data" / "reports" / f"contest8_{name}_{TAG}.json"
        save_report(report, out)
        reports[name] = report
        print(f"[{name}] {report.correct}/{report.total} = {report.accuracy:.1%} -> {out}")

    total_c = sum(r.correct for r in reports.values())
    total_t = sum(r.total for r in reports.values())
    acc = total_c / total_t if total_t else 0.0
    lines = [
        "# 命理师大赛 - 全量200题评测 (紫微斗数)",
        "",
        f"- 合计: **{total_c}/{total_t} = {acc:.1%}**",
        "- 配置: 紫微排盘(大限/流年/小限) + 紫微RAG + DeepSeek",
        "",
        "| 划分 | 正确/总数 | 准确率 |",
        "|------|-----------|--------|",
    ]
    for name in SPLITS:
        r = reports[name]
        lines.append(f"| {name} | {r.correct}/{r.total} | {r.accuracy:.1%} |")
    out_md = REPORT_DIR / "命理师大赛-全量200题-ziwei_only.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"total {total_c}/{total_t} = {acc:.1%}")
    print(f"report -> {out_md}")


if __name__ == "__main__":
    asyncio.run(main())
