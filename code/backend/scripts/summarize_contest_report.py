#!/usr/bin/env python
"""Print accuracy and wrong-answer list from a contest8 benchmark JSON report."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import load_split


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--md-out", type=Path, default=None)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    split = report["split"]
    by_id = {q.question_id: q for q in load_split(split)}  # type: ignore[arg-type]

    wrong = [r for r in report["results"] if not r["correct"]]
    errors = [r for r in report["results"] if r.get("error")]

    lines: list[str] = []
    lines.append(f"# Contest8 {split} 评测摘要")
    lines.append("")
    lines.append(f"- 准确率: **{report['accuracy']:.1%}** ({report['correct']}/{report['total']})")
    lines.append(f"- 错题数: {len(wrong)}")
    if errors:
        lines.append(f"- API/运行错误: {len(errors)}")
    lines.append("")
    lines.append("## 错题列表")
    lines.append("")
    for idx, r in enumerate(wrong, start=1):
        q = by_id.get(r["question_id"])
        stem = q.question if q else "(题目未找到)"
        opts = q.options if q else []
        gold_letter = r["gold"]
        pred = r["predicted"] or "(无)"
        gold_text = ""
        if q and gold_letter:
            i = ord(gold_letter.upper()) - ord("A")
            if 0 <= i < len(opts):
                gold_text = opts[i]
        lines.append(f"### {idx}. {r['question_id']}")
        lines.append(f"- 题目: {stem}")
        lines.append(f"- 标准答案: {gold_letter} {gold_text}")
        lines.append(f"- 模型预测: {pred}")
        if r.get("error"):
            lines.append(f"- 错误: {r['error']}")
        lines.append("")

    text = "\n".join(lines)
    print(text)
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(text, encoding="utf-8")
        print(f"\n(wrote {args.md_out})", file=sys.stderr)


if __name__ == "__main__":
    main()
