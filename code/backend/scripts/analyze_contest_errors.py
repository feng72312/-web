#!/usr/bin/env python
"""
Analyze Contest8 benchmark results by question theme: accuracy, strengths, errors.

Output markdown to d:/ZY/report/
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import ContestQuestion, flatten_questions
from app.benchmark.contest8_rag import infer_question_theme

REPORTS_DIR = ROOT / "data" / "reports"
DEFAULT_OUT = Path(__file__).resolve().parents[3] / "report"

METHOD_LABELS = {
    "bazi_kg": "八字(知识图谱)",
    "bazi_full": "八字(知识图谱+命例RAG+fewshot)",
    "bazi_fewshot": "八字(知识图谱+fewshot)",
    "fusion": "八字+六爻融合",
    "liuyao_only": "六爻(时间卦)",
}


def load_questions_by_id() -> dict[str, ContestQuestion]:
    items = flatten_questions([2021, 2022, 2023, 2024, 2025])
    return {q.question_id: q for q in items}


def option_text(q: ContestQuestion, letter: str) -> str:
    if not letter:
        return ""
    i = ord(letter.upper()) - ord("A")
    if 0 <= i < len(q.options):
        return q.options[i]
    return ""


def load_merged_results(method: str, reports_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for split in ("train", "val", "test"):
        path = reports_dir / f"contest8_{split}_{method}.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for r in data.get("results", []):
            row = dict(r)
            row["split"] = split
            rows.append(row)
    return rows


def analyze(rows: list[dict], by_id: dict[str, ContestQuestion]) -> dict:
    theme_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"correct": 0, "total": 0}
    )
    year_stats: dict[int, dict[str, int]] = defaultdict(
        lambda: {"correct": 0, "total": 0}
    )
    wrong_by_theme: dict[str, list[dict]] = defaultdict(list)
    correct_by_theme: dict[str, list[dict]] = defaultdict(list)
    pred_when_wrong: dict[str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )

    for r in rows:
        qid = r["question_id"]
        q = by_id.get(qid)
        if not q:
            continue
        theme = infer_question_theme(q.question)
        ok = bool(r.get("correct"))
        year = int(r.get("year", q.year))
        pred = str(r.get("predicted") or "")
        gold = str(r.get("gold") or "")

        theme_stats[theme]["total"] += 1
        year_stats[year]["total"] += 1
        if ok:
            theme_stats[theme]["correct"] += 1
            year_stats[year]["correct"] += 1
            if len(correct_by_theme[theme]) < 3:
                correct_by_theme[theme].append(
                    {"r": r, "q": q, "theme": theme}
                )
        else:
            theme_stats[theme]["correct"] += 0
            if len(wrong_by_theme[theme]) < 8:
                wrong_by_theme[theme].append({"r": r, "q": q, "theme": theme})
            if pred:
                pred_when_wrong[theme][pred] += 1

    return {
        "theme_stats": dict(theme_stats),
        "year_stats": dict(year_stats),
        "wrong_by_theme": dict(wrong_by_theme),
        "correct_by_theme": dict(correct_by_theme),
        "pred_when_wrong": dict(pred_when_wrong),
        "total": len(rows),
        "correct": sum(1 for r in rows if r.get("correct")),
    }


def theme_insight(theme: str, acc: float, total: int) -> str:
    if total < 3:
        return "样本较少, 仅供参考."
    if acc >= 0.45:
        return "相对强项: 题干信息可能与格局/十神线索较易对应."
    if acc >= 0.30:
        return "接近整体水平: 需结合大运流年细节, 模型仍易混淆相近选项."
    if acc >= 0.20:
        return "偏弱: 常需精确应期或事件次序, 单看本命盘+通用知识难以区分选项."
    return "明显偏弱: 多属具体流年/健康/官非等应期题, 或选项表述接近导致误判."


def render_markdown(
    method: str,
    stats: dict,
    by_id: dict[str, ContestQuestion],
) -> str:
    label = METHOD_LABELS.get(method, method)
    total = stats["total"]
    correct = stats["correct"]
    acc = correct / total if total else 0.0
    lines: list[str] = []

    lines.append("# 全球命理师大赛真题 - 对错与题型分析")
    lines.append("")
    lines.append(f"评测方式: **{label}** (`{method}`)")
    lines.append("")
    lines.append(
        "题库: `命理师大赛试题/历年全球命理师大赛试题与答案整理.md` "
        "(2021-2025, 200 题四选一)"
    )
    lines.append("")
    lines.append(f"- **总准确率**: {acc:.1%} ({correct}/{total})")
    lines.append("- 随机猜题基线约 25%")
    lines.append("- 题型由题干关键词自动归类 (与评测 RAG 主题规则一致)")
    lines.append("")

    lines.append("## 一、按题型准确率")
    lines.append("")
    lines.append("| 题型 | 对/总 | 准确率 | 相对整体 | 简要说明 |")
    lines.append("|------|-------|--------|----------|----------|")
    overall = acc
    ranked = sorted(
        stats["theme_stats"].items(),
        key=lambda x: (
            x[1]["correct"] / x[1]["total"] if x[1]["total"] else 0
        ),
        reverse=True,
    )
    for theme, s in ranked:
        c, n = s["correct"], s["total"]
        a = c / n if n else 0.0
        delta = a - overall
        sign = "+" if delta >= 0 else ""
        insight = theme_insight(theme, a, n)
        lines.append(
            f"| {theme} | {c}/{n} | {a:.1%} | {sign}{delta:.1%} | {insight} |"
        )
    lines.append("")

    lines.append("## 二、为什么「对」—— 题型强项归纳")
    lines.append("")
    best = [t for t, s in ranked if s["total"] >= 5 and s["correct"] / s["total"] >= 0.35]
    if best:
        lines.append("正确率高于 35% 且样本>=5 的题型: " + ", ".join(best) + ".")
        lines.append("")
        lines.append("可能原因:")
        lines.append("")
        lines.append("1. **家庭出身 / 性格外貌**: 多与静态本命信息相关, 知识图谱调候/十神描述可部分对齐.")
        lines.append("2. **学历 / 职业财运**: 部分题考查长期趋势, 结构化大运线索有一定帮助.")
        lines.append("3. 答对题中模型多能锁定**唯一较合理**选项, 而非在两项近似描述间摇摆.")
    else:
        lines.append("暂无显著强项题型 (均接近或低于整体准确率).")
    lines.append("")

    for theme, samples in sorted(stats["correct_by_theme"].items()):
        if not samples:
            continue
        lines.append(f"### 答对示例: {theme}")
        lines.append("")
        for item in samples[:2]:
            r, q = item["r"], item["q"]
            g, p = r["gold"], r.get("predicted", "")
            lines.append(f"- `{r['question_id']}` ({r.get('split')}, {r.get('year')})")
            lines.append(f"  - 题: {q.question}")
            lines.append(f"  - 金标 {g}: {option_text(q, g)}")
            lines.append(f"  - 预测 {p}: {option_text(q, p)}")
        lines.append("")

    lines.append("## 三、为什么「错」—— 题型弱项与错因")
    lines.append("")
    worst = [t for t, s in ranked if s["total"] >= 5 and s["correct"] / s["total"] < 0.25]
    if worst:
        lines.append("正确率低于 25% 且样本>=5 的题型: " + ", ".join(worst) + ".")
    lines.append("")
    lines.append("共性错因 (基于统计与题目形态, 非逐题人工断卦):")
    lines.append("")
    lines.append("1. **流年事件 / 应期**: 问「哪一年」「何时」, 需大运流年引动, 当前仅结构化本命+知识节点, 年份易错.")
    lines.append("2. **婚姻感情 / 子女**: 选项常描述次序(结婚/离婚/再婚)或次数, 需事件链推理, 易与相近选项混淆.")
    lines.append("3. **健康疾病 / 官非**: 低频具体事件, 训练数据与图谱覆盖不足, 模型倾向猜常见项.")
    lines.append("4. **四选一干扰**: 两项表述接近时, 模型随机偏向某一字母, 导致「差一项」错误.")
    lines.append("5. **LLM 非确定性**: 同配置重跑选项可能变化, 边界题不稳定.")
    lines.append("")

    lines.append("### 各题型错题分布 (预测字母频次)")
    lines.append("")
    for theme, _ in sorted(
        ranked, key=lambda x: x[1]["correct"] / x[1]["total"] if x[1]["total"] else 0
    ):
        dist = stats["pred_when_wrong"].get(theme, {})
        if not dist:
            continue
        parts = ", ".join(f"{k}:{v}" for k, v in sorted(dist.items()))
        s = stats["theme_stats"][theme]
        lines.append(
            f"- **{theme}** (错 {s['total']-s['correct']} 题): 预测字母 {parts}"
        )
    lines.append("")

    lines.append("## 四、按年份")
    lines.append("")
    lines.append("| 年份 | 对/总 | 准确率 |")
    lines.append("|------|-------|--------|")
    for year in sorted(stats["year_stats"]):
        s = stats["year_stats"][year]
        c, n = s["correct"], s["total"]
        lines.append(f"| {year} | {c}/{n} | {c/n:.1%} |")
    lines.append("")

    lines.append("## 五、分题型错题明细 (抽样)")
    lines.append("")
    for theme, _ in sorted(
        ranked, key=lambda x: x[1]["correct"] / x[1]["total"] if x[1]["total"] else 0
    ):
        wrongs = stats["wrong_by_theme"].get(theme, [])
        if not wrongs:
            continue
        s = stats["theme_stats"][theme]
        lines.append(f"### {theme} (共错 {s['total']-s['correct']} 题, 示例如下)")
        lines.append("")
        for item in wrongs[:5]:
            r, q = item["r"], item["q"]
            g, p = r["gold"], r.get("predicted") or "-"
            lines.append(f"#### `{r['question_id']}`")
            lines.append("")
            lines.append(f"- 划分: {r.get('split')} / {r.get('year')}")
            lines.append(f"- **题目**: {q.question}")
            lines.append("")
            lines.append("| 选项 | 内容 |")
            lines.append("|------|------|")
            for i, opt in enumerate(q.options):
                letter = chr(ord("A") + i)
                mark = []
                if letter == g:
                    mark.append("金标")
                if letter == p:
                    mark.append("预测")
                tag = f" ({', '.join(mark)})" if mark else ""
                lines.append(f"| {letter} | {opt}{tag} |")
            lines.append("")
            lines.append(
                f"- **错因简述**: 金标为 {g}, 模型选 {p}; "
                f"{'选项表述接近' if g != p else '未给出有效预测'}."
            )
            lines.append("")
        lines.append("")

    lines.append("## 六、改进方向 (针对本评测配置)")
    lines.append("")
    lines.append("1. 流年/应期类题: 在提示中强制列出相关大运、流年与冲合刑害后再选字母.")
    lines.append("2. 婚姻子女链: 增加「事件时间线」推理步骤, 避免只看配偶星静态描述.")
    lines.append("3. 启用命例 RAG + few-shot (`bazi_full`) 对弱项题型做对照实验.")
    lines.append("4. 固定 temperature=0 或多次投票, 降低随机波动.")
    lines.append("5. 不建议大赛 MCQ 默认接入六爻时间卦 (同人 5 题同卦, 实测易拉低准确率).")
    lines.append("")
    lines.append(
        f"原始数据: `code/backend/data/reports/contest8_{{split}}_{method}.json`"
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", default="bazi_kg", choices=list(METHOD_LABELS))
    parser.add_argument("--reports-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = load_merged_results(args.method, args.reports_dir)
    if not rows:
        print(f"no reports for method={args.method}", file=sys.stderr)
        sys.exit(1)

    by_id = load_questions_by_id()
    stats = analyze(rows, by_id)
    md = render_markdown(args.method, stats, by_id)

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"命理师大赛-真题错因分析-{args.method}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"wrote {out_path} ({stats['correct']}/{stats['total']})")


if __name__ == "__main__":
    main()
