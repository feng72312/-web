#!/usr/bin/env python
"""Print Contest8 multi-method benchmark completion status."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "reports"
METHODS = ["bazi_kg", "bazi_fewshot", "bazi_full", "fusion", "liuyao_only"]
SPLITS = ["train", "val", "test"]


def main() -> None:
    done = 0
    missing = 0
    print("Contest8 reports:", REPORTS)
    print()
    for method in METHODS:
        for split in SPLITS:
            path = REPORTS / f"contest8_{split}_{method}.json"
            if path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                acc = data.get("accuracy", 0) * 100
                print(
                    f"OK   {split:5} {method:12} "
                    f"{data.get('correct', '?')}/{data.get('total', '?')} ({acc:.1f}%)"
                )
                done += 1
            else:
                print(f"--   {split:5} {method:12} (missing)")
                missing += 1
    print()
    print(f"done={done} missing={missing} total={done + missing}")


if __name__ == "__main__":
    main()
