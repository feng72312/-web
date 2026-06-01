#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "reports" / "contest8_liunian_broad.json"
report = json.loads(path.read_text(encoding="utf-8"))
by: dict[str, dict[str, int]] = defaultdict(lambda: {"c": 0, "t": 0})
for row in report["results"]:
    theme = row["theme"]
    by[theme]["t"] += 1
    if row["correct"]:
        by[theme]["c"] += 1
print(f"total {report['correct']}/{report['total']} = {report['accuracy']:.1%}")
for theme, v in sorted(by.items(), key=lambda x: -(x[1]["c"] / max(x[1]["t"], 1))):
    acc = v["c"] / v["t"] if v["t"] else 0
    print(f"  {theme}: {v['c']}/{v['t']} = {acc:.1%}")
