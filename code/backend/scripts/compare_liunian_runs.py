#!/usr/bin/env python
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
strict = json.loads((ROOT / "data/reports/contest8_liunian_strict.json").read_text(encoding="utf-8"))
broad = {
    r["question_id"]: r
    for r in json.loads((ROOT / "data/reports/contest8_liunian_broad.json").read_text(encoding="utf-8"))[
        "results"
    ]
}
print(f"strict: {strict['correct']}/{strict['total']} = {strict['accuracy']:.1%}")
for r in strict["results"]:
    b = broad.get(r["question_id"], {})
    if r.get("correct") != b.get("correct"):
        tag = "NEW_OK" if r.get("correct") else "LOST"
        print(
            tag,
            r["question_id"],
            "pred",
            b.get("predicted"),
            "->",
            r.get("predicted"),
            "gold",
            r.get("gold"),
        )
