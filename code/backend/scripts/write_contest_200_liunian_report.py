#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "reports"
REPORT_DIR = ROOT.parents[1] / "report"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import flatten_questions
from app.benchmark.contest8_rag import infer_question_theme

TAG = "bazi_liunian"
SPLITS = ("train", "val", "test")
PRIOR_TAG = "bazi_fewshot"


def load_report(name: str) -> dict:
    return json.loads((REPORTS / name).read_text(encoding="utf-8"))


def main() -> None:
    total_c = total_t = 0
    prior_c = prior_t = 0
    split_rows = []
    all_results = []
    by_id = {
        q.question_id: q.question
        for q in flatten_questions([2021, 2022, 2023, 2024, 2025])
    }

    for sp in SPLITS:
        r = load_report(f"contest8_{sp}_{TAG}.json")
        split_rows.append((sp, r["correct"], r["total"], r["accuracy"]))
        total_c += r["correct"]
        total_t += r["total"]
        all_results.extend(r.get("results", []))
        p_path = REPORTS / f"contest8_{sp}_{PRIOR_TAG}.json"
        if p_path.is_file():
            p = json.loads(p_path.read_text(encoding="utf-8"))
            prior_c += p["correct"]
            prior_t += p["total"]

    summary = {
        "tag": TAG,
        "correct": total_c,
        "total": total_t,
        "accuracy": total_c / total_t if total_t else 0,
    }
    (REPORTS / f"contest8_all_{TAG}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    by_theme: dict[str, list] = defaultdict(list)
    for row in all_results:
        qtext = by_id.get(row.get("question_id", ""), "")
        by_theme[infer_question_theme(qtext)].append(row)

    lines = [
        "# 命理师大赛 - 全量200题评测 (流年增强管线)",
        "",
        f"- 合计: **{total_c}/{total_t} = {summary['accuracy']:.1%}**",
        "- 配置: 知识图谱(dayun+liunian) + fewshot + 命例RAG(若8100可用)",
        "- 流年事件/含公历年份题干: 规则预排除 + 逐选项推理",
        "",
        "| 划分 | 正确/总数 | 准确率 |",
        "|------|-----------|--------|",
    ]
    for sp, c, t, acc in split_rows:
        lines.append(f"| {sp} | {c}/{t} | {acc:.1%} |")

    if prior_t:
        lines.extend(
            [
                "",
                f"对比 prior `{PRIOR_TAG}`: **{prior_c}/{prior_t} = {prior_c/prior_t:.1%}** "
                f"(delta **{total_c - prior_c:+d}** 题)",
            ]
        )
    no_rag_v = REPORTS / "contest8_val_bazi_liunian_no_rag.json"
    if no_rag_v.is_file():
        lines.extend(
            [
                "",
                "说明: train 为无 RAG 首轮; val/test 已用 RAG(8100)重跑.",
                "无 RAG 备份: `contest8_val_bazi_liunian_no_rag.json`, "
                "`contest8_test_bazi_liunian_no_rag.json`.",
            ]
        )

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
    if prior_t:
        print(f"prior {prior_c}/{prior_t} = {prior_c/prior_t:.1%}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
