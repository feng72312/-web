"""Compare marriage subset reports by marriageSubtheme."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import flatten_questions
from app.core.knowledge.marriage_subtheme import infer_marriage_subtheme


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _question_lookup() -> dict[str, tuple[str, list[str]]]:
    rows = flatten_questions([2021, 2022, 2023, 2024, 2025])
    return {
        q.question_id: (q.question, list(q.options or []))
        for q in rows
        if getattr(q, "question_id", None)
    }


def resolve_subtheme(row: dict, lookup: dict[str, tuple[str, list[str]]]) -> str:
    st = row.get("marriageSubtheme") or row.get("marriage_subtheme")
    if st:
        return st
    qid = row.get("question_id", "")
    if qid in lookup:
        question, options = lookup[qid]
        inferred = infer_marriage_subtheme(question, options)
        if inferred:
            return inferred
    return "unknown"


def by_subtheme(data: dict, lookup: dict[str, tuple[str, list[str]]]) -> dict[str, dict]:
    groups: dict[str, dict] = defaultdict(lambda: {"total": 0, "correct": 0, "wrong_ids": []})
    for row in data["results"]:
        st = resolve_subtheme(row, lookup)
        groups[st]["total"] += 1
        if row.get("correct"):
            groups[st]["correct"] += 1
        else:
            groups[st]["wrong_ids"].append(row["question_id"])
    return dict(groups)


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "data" / "reports"
    tags = sys.argv[1:] or ["p2", "p4", "p5"]
    files = {
        "p2": root / "contest8_sub_hunyin_p2.json",
        "p4": root / "contest8_sub_hunyin_p4.json",
        "p5": root / "contest8_sub_hunyin_p5.json",
        "p6": root / "contest8_sub_hunyin_p6.json",
    }
    per: dict[str, dict] = {}
    all_st: set[str] = set()
    lookup = _question_lookup()
    for tag in tags:
        path = files.get(tag)
        if path is None or not path.exists():
            print(f"skip {tag}: missing")
            continue
        data = load(path)
        per[tag] = {
            "correct": data["correct"],
            "total": data["total"],
            "by": by_subtheme(data, lookup),
        }
        all_st |= set(per[tag]["by"].keys())

    print("Overall:")
    for tag in tags:
        if tag not in per:
            continue
        x = per[tag]
        pct = 100.0 * x["correct"] / x["total"]
        print(f"  {tag}: {x['correct']}/{x['total']} = {pct:.1f}%")

    print("\nBy marriageSubtheme (correct/total):")
    header = ["subtheme"] + [t for t in tags if t in per]
    print("  " + " | ".join(header))
    for st in sorted(all_st):
        cells = [st]
        for tag in tags:
            if tag not in per:
                continue
            b = per[tag]["by"].get(st, {"correct": 0, "total": 0})
            cells.append(f"{b['correct']}/{b['total']}")
        print("  " + " | ".join(cells))


if __name__ == "__main__":
    main()
