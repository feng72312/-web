# -*- coding: utf-8 -*-
"""Merge zhuge qian 231-384 from traditional reference into zhuge_qian.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BUNDLED = DATA_DIR / "zhuge_384_reference.txt"
REFERENCE = BUNDLED
OUT = DATA_DIR / "zhuge_qian.json"


def to_simplified(text: str) -> str:
    try:
        from opencc import OpenCC

        return OpenCC("t2s").convert(text)
    except Exception:
        return text


def normalize_poem(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("，", "，").replace("。", "。")
    return to_simplified(text)


def parse_reference(raw: str) -> dict[str, str]:
    qian: dict[str, str] = {}
    parts = re.split(r"第(\d+)簽", raw)
    # parts[0] is header; then pairs (num, block)
    index = 1
    while index + 1 < len(parts):
        num = int(parts[index])
        block = parts[index + 1]
        index += 2
        m = re.search(r"簽詩[：:](.*?)解簽", block, re.DOTALL)
        if not m:
            continue
        poem = normalize_poem(m.group(1))
        if poem and num >= 231:
            qian[str(num)] = poem
    return qian


def main() -> None:
    ref_path = REFERENCE if REFERENCE.exists() else BUNDLED
    if not ref_path.exists():
        raise SystemExit(f"reference not found: {ref_path}")

    raw = ref_path.read_text(encoding="utf-8")
    new_entries = parse_reference(raw)
    if len(new_entries) < 100:
        raise SystemExit(f"parsed too few entries: {len(new_entries)}")

    payload = json.loads(OUT.read_text(encoding="utf-8"))
    existing = payload.get("qian", {})
    merged = dict(existing)
    added = 0
    for key, poem in new_entries.items():
        if key not in merged or not merged[key].strip():
            merged[key] = poem
            added += 1

    payload["qian"] = merged
    payload["maxNo"] = 384
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"merged: +{added} new/empty slots, total keys={len(merged)}")
    missing = [n for n in range(1, 385) if str(n) not in merged]
    if missing:
        print(f"still missing ({len(missing)}): {missing[:20]}...")


if __name__ == "__main__":
    main()
