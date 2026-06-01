#!/usr/bin/env python
"""Summarize 200-question contest reports and compare to prior bazi_fewshot."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "reports"


def load(name: str) -> dict | None:
    p = REPORTS / name
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def summarize(report: dict) -> str:
    return f"{report['correct']}/{report['total']} = {report['accuracy']:.1%}"


def main() -> None:
    tag = sys.argv[1] if len(sys.argv) > 1 else "bazi_liunian"
    splits = ("train", "val", "test")
    total_c = total_t = 0
    print(f"tag={tag}")
    for sp in splits:
        r = load(f"contest8_{sp}_{tag}.json")
        if not r:
            print(f"  {sp}: missing")
            continue
        print(f"  {sp}: {summarize(r)}")
        total_c += r["correct"]
        total_t += r["total"]
    if total_t:
        print(f"  ALL: {total_c}/{total_t} = {total_c/total_t:.1%}")
    prior = load("contest8_train_bazi_fewshot.json")
    if prior and total_t:
        old_c = old_t = 0
        for sp in splits:
            o = load(f"contest8_{sp}_bazi_fewshot.json")
            if o:
                old_c += o["correct"]
                old_t += o["total"]
        if old_t:
            print(f"  prior bazi_fewshot: {old_c}/{old_t} = {old_c/old_t:.1%}")
            print(f"  delta: {total_c - old_c:+d} questions")


if __name__ == "__main__":
    main()
