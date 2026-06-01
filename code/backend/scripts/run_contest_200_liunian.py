#!/usr/bin/env python
"""Run full 200 Contest8 MCQ with kg+RAG+fewshot and liunian reasoning pipeline."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT.parents[1] / "report"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import split_summary
from app.benchmark.contest8_eval import run_eval, save_report
from app.benchmark.contest8_rag import infer_question_theme

TAG = "bazi_liunian"
SPLITS = ("train", "val", "test")


async def main() -> None:
    print("dataset:", split_summary())
    print("config: knowledge + case RAG + fewshot + liunian reasoning/exclusion on event questions")
    reports = {}
    for name in SPLITS:
        report = await run_eval(
            name,  # type: ignore[arg-type]
            use_knowledge=True,
            use_case_rag=True,
            use_fewshot=True,
        )
        out = ROOT / "data" / "reports" / f"contest8_{name}_{TAG}.json"
        save_report(report, out)
        reports[name] = report
        print(f"[{name}] {report.correct}/{report.total} = {report.accuracy:.1%} -> {out}")

    total_c = sum(r.correct for r in reports.values())
    total_t = sum(r.total for r in reports.values())
    summary = {
        "tag": TAG,
        "total": total_t,
        "correct": total_c,
        "accuracy": total_c / total_t if total_t else 0,
        "splits": {
            k: {"correct": v.correct, "total": v.total, "accuracy": v.accuracy}
            for k, v in reports.items()
        },
    }
    summary_path = ROOT / "data" / "reports" / f"contest8_all_{TAG}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# 命理师大赛 - 全量200题评测 (流年增强管线)",
        "",
        f"- 合计: **{total_c}/{total_t} = {summary['accuracy']:.1%}**",
        "- 配置: 八字知识图谱(dayun+liunian) + 命例RAG + fewshot",
        "- 流年事件/含XXXX年题干: 规则预排除 + 逐选项推理 + 末行答案",
        "- 随机基线约 25%",
        "",
        "| 划分 | 正确/总数 | 准确率 |",
        "|------|-----------|--------|",
    ]
    for sp in SPLITS:
        s = summary["splits"][sp]
        lines.append(f"| {sp} | {s['correct']}/{s['total']} | {s['accuracy']:.1%} |")

    by_theme: dict[str, list] = {}
    for sp, rep in reports.items():
        for row in rep.to_dict()["results"]:
            theme = infer_question_theme(row.get("question", ""))
            by_theme.setdefault(theme, []).append(row)

    lines.extend(["", "## 按题型", "", "| 题型 | 对/总 | 准确率 |", "|------|-------|--------|"])
    for theme, rows in sorted(
        by_theme.items(),
        key=lambda x: sum(1 for r in x[1] if r.get("correct")) / max(len(x[1]), 1),
        reverse=True,
    ):
        c = sum(1 for r in rows if r.get("correct"))
        lines.append(f"| {theme} | {c}/{len(rows)} | {c/len(rows):.1%} |")

    md_path = REPORT_DIR / "命理师大赛-全量200题-bazi_liunian.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"ALL {total_c}/{total_t} = {summary['accuracy']:.1%}")
    print(f"wrote {summary_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    asyncio.run(main())
