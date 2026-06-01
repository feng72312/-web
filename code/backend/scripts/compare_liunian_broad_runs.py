#!/usr/bin/env python
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> dict:
    return json.loads((ROOT / "data" / "reports" / name).read_text(encoding="utf-8"))


def main() -> None:
    new = load("contest8_liunian_broad.json")
    try:
        old = load("contest8_liunian_broad_before_luck_chart_fix.json")
    except FileNotFoundError:
        print("no backup before_luck_chart_fix")
        return
    by_old = {r["question_id"]: r for r in old["results"]}
    imp, wor, same = [], [], 0
    for r in new["results"]:
        o = by_old.get(r["question_id"])
        if not o:
            continue
        if r["correct"] and not o.get("correct"):
            imp.append(r["question_id"])
        elif not r["correct"] and o.get("correct"):
            wor.append(r["question_id"])
        if r.get("predicted") == o.get("predicted"):
            same += 1
    print(f"old {old['correct']}/{old['total']} = {old['accuracy']:.1%}")
    print(f"new {new['correct']}/{new['total']} = {new['accuracy']:.1%}")
    print(f"improved {len(imp)}: {', '.join(imp[:12])}{'...' if len(imp)>12 else ''}")
    print(f"worsened {len(wor)}: {', '.join(wor[:12])}{'...' if len(wor)>12 else ''}")
    print(f"same letter {same}")


if __name__ == "__main__":
    main()
