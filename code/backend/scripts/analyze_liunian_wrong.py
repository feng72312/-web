#!/usr/bin/env python
"""Summarize wrong answers from contest8_liunian_broad.json."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_chart import build_chart_for_question
from app.benchmark.contest8_dataset import ContestQuestion, flatten_questions
from app.core.knowledge.target_year_block import build_target_year_block
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.luck_prompt_util import extract_years_from_question

REPORT = ROOT / "data" / "reports" / "contest8_liunian_broad.json"
PRIOR = [
    ROOT / "data/reports/contest8_train_bazi_kg.json",
    ROOT / "data/reports/contest8_val_bazi_kg.json",
    ROOT / "data/reports/contest8_test_bazi_kg.json",
]


def load_prior() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in PRIOR:
        if not p.is_file():
            continue
        for r in json.loads(p.read_text(encoding="utf-8")).get("results", []):
            out[r["question_id"]] = r
    return out


def main() -> None:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    prior = load_prior()
    wrong = [r for r in data["results"] if not r["correct"]]
    print(f"wrong {len(wrong)}/{data['total']}")
    by_theme: dict[str, list] = defaultdict(list)
    for r in wrong:
        by_theme[r["theme"]].append(r)
    print("\nby theme (wrong count):")
    for t, rows in sorted(by_theme.items(), key=lambda x: -len(x[1])):
        print(f"  {t}: {len(rows)}")

    pred_vs_gold = Counter()
    for r in wrong:
        pred_vs_gold[(r.get("predicted") or "?") + "->" + r["gold"]] += 1
    print("\ntop pred->gold on wrong:")
    for k, v in pred_vs_gold.most_common(8):
        print(f"  {k}: {v}")

    prior_wrong = prior_right = 0
    for r in wrong:
        old = prior.get(r["question_id"])
        if not old:
            continue
        if old.get("correct"):
            prior_right += 1
        else:
            prior_wrong += 1
    print(f"\nprior bazi_kg: was right {prior_right}, was also wrong {prior_wrong}")

    # structural: target year block empty?
    by_id = {q.question_id: q for q in flatten_questions([2021, 2022, 2023, 2024, 2025])}
    empty_block = 0
    no_year_in_chart = 0
    svc = get_knowledge_service()
    samples: list[str] = []
    for r in wrong[:46]:
        q = by_id.get(r["question_id"])
        if not q:
            continue
        chart = build_chart_for_question(q)
        years = extract_years_from_question(q.question)
        compressed = None
        if svc.enabled:
            compressed = svc.resolve_for_chart(chart, question=q.question)
        block = build_target_year_block(chart, q.question, compressed)
        if not block or "未落入大运表" in block:
            empty_block += 1
        if years:
            found = any(
                ln.get("year") == y
                for dy in chart.get("dayun") or []
                for ln in dy.get("liunian") or []
                for y in years
            )
            if not found:
                no_year_in_chart += 1
        if len(samples) < 5 and r["theme"] == "流年事件":
            samples.append(r["question_id"])
    print(f"\nwrong with empty/broken target block: {empty_block}")
    print(f"wrong with year not in chart liunian table: {no_year_in_chart}")
    print("sample 流年事件 wrong ids:", ", ".join(samples))


if __name__ == "__main__":
    main()
