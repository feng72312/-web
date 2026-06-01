#!/usr/bin/env python
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    new = json.loads(
        (ROOT / "data/reports/contest8_liunian_strict.json").read_text(encoding="utf-8")
    )
    backups = [
        "contest8_liunian_strict_before_rule_exclusion.json",
        "contest8_liunian_strict_before_reasoning.json",
        "contest8_liunian_strict_before_votes3.json",
        "contest8_liunian_broad.json",
    ]
    print(f"new strict votes={new.get('votes',1)}: {new['correct']}/{new['total']} = {new['accuracy']:.1%}")
    for name in backups:
        path = ROOT / "data/reports" / name
        if not path.is_file():
            continue
        old_all = json.loads(path.read_text(encoding="utf-8"))
        by_id = {r["question_id"]: r for r in old_all["results"]}
        imp, wor = [], []
        for r in new["results"]:
            o = by_id.get(r["question_id"])
            if not o:
                continue
            if r["correct"] and not o.get("correct"):
                imp.append(r["question_id"])
            elif not r["correct"] and o.get("correct"):
                wor.append(r["question_id"])
        label = name.replace(".json", "")
        if name == "contest8_liunian_broad.json":
            c = sum(1 for r in new["results"] if r["correct"])
            print(f"vs broad same 19 ids: {c}/19 from broad subset")
        else:
            print(f"vs {label}: improved {len(imp)} worsened {len(wor)}")
            if imp:
                print("  +", ", ".join(imp))
            if wor:
                print("  -", ", ".join(wor))
    wrong = [r for r in new["results"] if not r["correct"]]
    print(f"\nwrong {len(wrong)}:")
    for r in wrong:
        letters = r.get("voteLetters") or []
        print(
            f"  {r['question_id']} gold={r['gold']} pred={r['predicted']} votes={letters}"
        )


if __name__ == "__main__":
    main()
