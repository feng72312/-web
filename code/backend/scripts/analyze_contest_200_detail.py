#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT.parents[1] / "report"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import flatten_questions
from app.benchmark.contest8_rag import infer_question_theme

TAG = "bazi_liunian"
SPLITS = ("train", "val", "test")


def main() -> None:
    by_id = {q.question_id: q for q in flatten_questions([2021, 2022, 2023, 2024, 2025])}
    correct_rows = []
    wrong_rows = []

    for sp in SPLITS:
        path = ROOT / "data" / "reports" / f"contest8_{sp}_{TAG}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for r in data["results"]:
            q = by_id.get(r["question_id"])
            row = {
                "split": sp,
                "question_id": r["question_id"],
                "year": r["year"],
                "gold": r["gold"],
                "predicted": r["predicted"],
                "correct": r["correct"],
                "theme": infer_question_theme(q.question if q else ""),
                "question": (q.question if q else "")[:100],
                "options": q.options if q else [],
            }
            if r["correct"]:
                correct_rows.append(row)
            else:
                wrong_rows.append(row)

    lines = [
        "# 命理师大赛 - 全量200题对错分析 (bazi_liunian)",
        "",
        f"- 对: **{len(correct_rows)}/200** | 错: **{len(wrong_rows)}/200**",
        "",
        "## 一、按划分",
        "",
        "| 划分 | 对 | 错 |",
        "|------|----|----|",
    ]
    for sp in SPLITS:
        c = sum(1 for x in correct_rows if x["split"] == sp)
        w = sum(1 for x in wrong_rows if x["split"] == sp)
        lines.append(f"| {sp} | {c} | {w} |")

    lines.extend(["", "## 二、按题型", "", "| 题型 | 对/总 | 准确率 |", "|------|-------|--------|"])
    by_theme_all: dict[str, list] = defaultdict(list)
    for row in correct_rows + wrong_rows:
        by_theme_all[row["theme"]].append(row)
    for theme, rows in sorted(
        by_theme_all.items(),
        key=lambda x: sum(1 for r in x[1] if r["correct"]) / max(len(x[1]), 1),
        reverse=True,
    ):
        c = sum(1 for r in rows if r["correct"])
        lines.append(f"| {theme} | {c}/{len(rows)} | {c/len(rows):.1%} |")

    lines.extend(["", "## 三、错题预测分布", ""])
    pred_gold = Counter((r["predicted"], r["gold"]) for r in wrong_rows)
    for (p, g), n in pred_gold.most_common(8):
        lines.append(f"- 预测 **{p}** 金标 **{g}**: {n} 题")

    lines.extend(["", "## 四、答对题目清单", ""])
    by_theme_c: dict[str, list] = defaultdict(list)
    for r in correct_rows:
        by_theme_c[r["theme"]].append(r)
    for theme in sorted(by_theme_c.keys()):
        lines.append(f"### {theme} ({len(by_theme_c[theme])}题)")
        for r in sorted(by_theme_c[theme], key=lambda x: (x["split"], x["question_id"])):
            opt_g = ""
            q = by_id.get(r["question_id"])
            if q and r["gold"]:
                idx = ord(r["gold"].upper()) - ord("A")
                if 0 <= idx < len(q.options):
                    opt_g = q.options[idx][:60]
            lines.append(
                f"- `{r['question_id']}` [{r['split']}] {r['question']} "
                f"-> **{r['gold']}** {opt_g}"
            )
        lines.append("")

    lines.extend(["", "## 五、错题清单与原因归纳", ""])
    by_theme_w: dict[str, list] = defaultdict(list)
    for r in wrong_rows:
        by_theme_w[r["theme"]].append(r)

    reason_map = {
        "流年事件": "应期/十神与选项故事难对齐; 相近事件互混(财/官非/健康)",
        "婚姻感情": "婚否+学历/次序组合题, 常只对一半维度",
        "职业财运": "大运十年与流年混用; 选项职业描述接近",
        "健康疾病": "病种类选项语义相近(如乳癌vs妇科病)",
        "综合": "非单年应期, 信息面宽, 规则预排除未覆盖",
        "官非": "样本少; 官杀流年线索不足时易偏 D",
        "学历": "印星流年与学校层级选项难区分",
        "性格外貌": "描述性选项, 十神线索弱",
        "子女": "食神伤官子女星与年份对应不稳",
        "田宅": "房产流年样本少",
        "家庭出身": "父母星+大运, 非纯流年模板",
    }

    for theme in sorted(by_theme_w.keys()):
        rows = by_theme_w[theme]
        lines.append(f"### {theme} ({len(rows)}题错) - {reason_map.get(theme, '选项接近或线索不足')}")
        for r in sorted(rows, key=lambda x: (x["split"], x["question_id"])):
            q = by_id.get(r["question_id"])
            opt_g = opt_p = ""
            if q:
                for letter, name in ((r["gold"], "g"), (r["predicted"], "p")):
                    if not letter or len(letter) != 1:
                        continue
                    idx = ord(letter.upper()) - ord("A")
                    if 0 <= idx < len(q.options):
                        if name == "g":
                            opt_g = q.options[idx][:50]
                        else:
                            opt_p = q.options[idx][:50]
            lines.append(
                f"- `{r['question_id']}` [{r['split']}] {r['question']}"
            )
            lines.append(f"  - 金标 **{r['gold']}** {opt_g} | 预测 **{r['predicted']}** {opt_p}")
        lines.append("")

    lines.extend(
        [
            "",
            "## 六、共性错因",
            "",
            "1. **LLM 波动**: 同配置 val/test 重跑可差 1-2 题.",
            "2. **偏 D**: 错题中预测 D 而金标为 A/B 仍较多.",
            "3. **流年题**: 有规则预排除时 strict 可达 47%, 全库 19 题中 9 对.",
            "4. **非流年题**: 仍用本命+图谱, 婚姻/综合/学历最难.",
            "5. **RAG**: train 无 RAG; val/test 重跑有 RAG 但整体未升.",
        ]
    )

    out = REPORT_DIR / "命理师大赛-全量200题对错分析-bazi_liunian.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")
    print(f"correct {len(correct_rows)} wrong {len(wrong_rows)}")


if __name__ == "__main__":
    main()
