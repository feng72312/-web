#!/usr/bin/env python
"""Aggregate Contest8 method reports into markdown under d:/ZY/report."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import load_split, split_summary

REPORTS_DIR = ROOT / "data" / "reports"
DEFAULT_OUT = Path(__file__).resolve().parents[3] / "report"

METHOD_ORDER = [
    "bazi_kg",
    "bazi_fewshot",
    "bazi_full",
    "fusion",
    "liuyao_only",
]

METHOD_LABELS = {
    "bazi_kg": "八字(知识图谱)",
    "bazi_fewshot": "八字(知识图谱+fewshot)",
    "bazi_full": "八字(知识图谱+命例RAG+fewshot)",
    "fusion": "八字+六爻融合",
    "liuyao_only": "六爻(时间卦)",
}

SPLIT_YEARS = {
    "train": "2021-2023",
    "val": "2024",
    "test": "2025",
}


def load_report(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def discover_reports() -> dict[tuple[str, str], dict]:
    found: dict[tuple[str, str], dict] = {}
    aliases = {
        "contest8_val_full": ("bazi_full", "val"),
        "contest8_test_full": ("bazi_full", "test"),
    }
    for path in sorted(REPORTS_DIR.glob("contest8_*.json")):
        name = path.stem
        if name in aliases:
            method, split = aliases[name]
            data = load_report(path)
            if data and "accuracy" in data:
                found[(method, split)] = data
            continue
        parts = name.split("_", 2)
        if len(parts) < 3:
            continue
        split = parts[1]
        method = parts[2]
        if split not in ("train", "val", "test"):
            continue
        if method in ("full", "baseline", "fewshot", "case", "rag"):
            continue
        data = load_report(path)
        if data and "accuracy" in data:
            found[(method, split)] = data
    return found


def year_stats(results: list[dict]) -> dict[int, tuple[int, int]]:
    by_year: dict[int, list[bool]] = defaultdict(list)
    for r in results:
        by_year[int(r["year"])].append(bool(r["correct"]))
    return {y: (sum(1 for c in cs if c), len(cs)) for y, cs in sorted(by_year.items())}


def person_stats(results: list[dict]) -> dict[str, tuple[int, int]]:
    by_person: dict[str, list[bool]] = defaultdict(list)
    for r in results:
        pid = r["question_id"].rsplit("-", 1)[0]
        by_person[pid].append(bool(r["correct"]))
    return {p: (sum(1 for c in cs if c), len(cs)) for p, cs in sorted(by_person.items())}


def build_wrong_section(
    report: dict,
    split: str,
    method: str,
    *,
    max_items: int = 15,
) -> list[str]:
    by_id = {q.question_id: q for q in load_split(split)}  # type: ignore[arg-type]
    wrong = [r for r in report.get("results", []) if not r.get("correct")]
    lines: list[str] = []
    for idx, r in enumerate(wrong[:max_items], start=1):
        q = by_id.get(r["question_id"])
        stem = q.question if q else r["question_id"]
        lines.append(
            f"{idx}. `{r['question_id']}` 金标 **{r['gold']}** 预测 **{r.get('predicted') or '-'}** | {stem[:60]}..."
        )
    if len(wrong) > max_items:
        lines.append(f"... 另有 {len(wrong) - max_items} 题见 JSON 报告")
    return lines


def render_markdown(
    reports: dict[tuple[str, str], dict],
    out_dir: Path,
    *,
    reports_dir: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    methods_present = sorted({m for m, _ in reports}, key=lambda x: METHOD_ORDER.index(x) if x in METHOD_ORDER else 99)
    splits_present = [s for s in ("train", "val", "test") if any((m, s) in reports for m in methods_present)]

    lines: list[str] = []
    lines.append("# 全球命理师大赛真题 - 算命方式对比评测")
    lines.append("")
    lines.append(f"生成时间: {now}")
    lines.append("")
    lines.append("题库与 `命理师大赛试题/历年全球命理师大赛试题与答案整理.md` 同源 (BaziQA Contest8, 2021-2025, 共 200 题).")
    lines.append("模型: DeepSeek `deepseek-chat`, 真实排盘与 API 调用, 非模拟数据.")
    lines.append("")
    lines.append("## 数据划分")
    lines.append("")
    lines.append("| 划分 | 年份 | 题数 |")
    lines.append("|------|------|------|")
    for split, n in split_summary().items():
        years = SPLIT_YEARS.get(split, "")
        lines.append(f"| {split} | {years} | {n} |")
    lines.append("| **合计** | 2021-2025 | **200** |")
    lines.append("")

    lines.append("## 方法说明")
    lines.append("")
    for mid in METHOD_ORDER:
        if mid not in methods_present:
            continue
        label = METHOD_LABELS.get(mid, mid)
        lines.append(f"- **{label}** (`{mid}`)")
    lines.append("")
    lines.append("随机四选一基线约 **25%**.")
    lines.append("")

    expected = [(m, s) for m in METHOD_ORDER for s in ("train", "val", "test")]
    missing = [f"{METHOD_LABELS.get(m, m)} / {s}" for m, s in expected if (m, s) not in reports]
    if missing:
        lines.append("## 评测进度")
        lines.append("")
        lines.append("以下组合尚未生成报告 (可运行 `python scripts/contest_methods_benchmark.py --split all --methods all`):")
        lines.append("")
        for item in missing:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## 总览准确率")
    lines.append("")
    header = "| 方法 | " + " | ".join(splits_present) + " | 合计 |"
    lines.append(header)
    lines.append("|" + "------|" * (len(splits_present) + 2))
    for method in METHOD_ORDER:
        if method not in methods_present:
            continue
        label = METHOD_LABELS.get(method, method)
        cells = []
        total_c = 0
        total_n = 0
        for split in splits_present:
            rep = reports.get((method, split))
            if rep:
                c, n = rep["correct"], rep["total"]
                cells.append(f"{c}/{n} ({rep['accuracy']:.1%})")
                total_c += c
                total_n += n
            else:
                cells.append("-")
        if total_n:
            cells.append(f"**{total_c}/{total_n} ({total_c/total_n:.1%})**")
        else:
            cells.append("-")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")

    lines.append("")
    lines.append("## 按年份 (合并各划分)")
    lines.append("")
    for method in METHOD_ORDER:
        if method not in methods_present:
            continue
        merged_results: list[dict] = []
        for split in splits_present:
            rep = reports.get((method, split))
            if rep:
                merged_results.extend(rep.get("results", []))
        if not merged_results:
            continue
        ys = year_stats(merged_results)
        label = METHOD_LABELS.get(method, method)
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| 年份 | 正确/总数 | 准确率 |")
        lines.append("|------|-----------|--------|")
        for year, (c, n) in ys.items():
            lines.append(f"| {year} | {c}/{n} | {c/n:.1%} |")
        lines.append("")

    lines.append("## 融合模式通道分解 (仅 fusion)")
    lines.append("")
    for split in splits_present:
        rep = reports.get(("fusion", split))
        if not rep:
            continue
        results = rep.get("results", [])
        if not results or "baziPred" not in results[0]:
            continue
        bazi_c = sum(1 for r in results if r.get("baziPred") == r["gold"])
        ly_c = sum(1 for r in results if r.get("liuyaoPred") == r["gold"])
        merged_c = rep["correct"]
        n = len(results)
        lines.append(
            f"- **{split} ({SPLIT_YEARS.get(split, '')})**: "
            f"合并 {merged_c}/{n}, 八字通道 {bazi_c}/{n}, 六爻通道 {ly_c}/{n}"
        )
    lines.append("")

    lines.append("## 各方法错题抽样 (val + test)")
    lines.append("")
    for method in METHOD_ORDER:
        if method not in methods_present:
            continue
        label = METHOD_LABELS.get(method, method)
        lines.append(f"### {label}")
        lines.append("")
        for split in ("val", "test"):
            rep = reports.get((method, split))
            if not rep:
                lines.append(f"*{split}: 无报告*")
                lines.append("")
                continue
            wrong_n = rep["total"] - rep["correct"]
            lines.append(f"**{split}** 错 {wrong_n} 题:")
            lines.append("")
            for row in build_wrong_section(rep, split, method):
                lines.append(row)
            lines.append("")

    lines.append("## 结论与建议")
    lines.append("")
    lines.append("1. **大赛 MCQ 以八字单通道为主**; 命例 RAG + few-shot 为当前项目完整配置 (`bazi_full`).")
    lines.append("2. **六爻时间卦** 对同一命主 5 题共用一卦, 区分度低, 融合合并易拉低八字答对题.")
    lines.append("3. 评测波动较大 (同配置重复跑选项可能不同), 结论宜结合多次运行或固定 temperature.")
    lines.append("")
    lines.append(f"原始 JSON: `{reports_dir.as_posix()}/contest8_{{split}}_{{method}}.json`")
    lines.append("")

    main_path = out_dir / "命理师大赛-算命方式对比.md"
    main_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {main_path}")

    # Per-method detail for bazi_full if available
    for method in ("bazi_full",):
        parts = []
        for split in ("train", "val", "test"):
            rep = reports.get((method, split))
            if not rep:
                continue
            parts.append(f"## {split} ({SPLIT_YEARS.get(split, '')})")
            parts.append(f"准确率: {rep['accuracy']:.1%} ({rep['correct']}/{rep['total']})")
            parts.append("")
            ps = person_stats(rep.get("results", []))
            parts.append("| 命例 | 得分 |")
            parts.append("|------|------|")
            for pid, (c, n) in ps.items():
                parts.append(f"| `{pid}` | {c}/{n} |")
            parts.append("")
        if parts:
            detail_path = out_dir / "命理师大赛-八字主流程-分命例.md"
            detail_path.write_text(
                "# 八字主流程 (bazi_full) 分命例得分\n\n"
                + "\n".join(parts),
                encoding="utf-8",
            )
            print(f"wrote {detail_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=REPORTS_DIR,
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
    )
    args = parser.parse_args()
    reports = _discover_in_dir(args.reports_dir)
    if not reports:
        print("no reports found", file=sys.stderr)
        sys.exit(1)
    render_markdown(reports, args.out_dir, reports_dir=args.reports_dir)


def _discover_in_dir(reports_dir: Path) -> dict[tuple[str, str], dict]:
    global REPORTS_DIR
    old = REPORTS_DIR
    REPORTS_DIR = reports_dir
    try:
        return discover_reports()
    finally:
        REPORTS_DIR = old


if __name__ == "__main__":
    main()
