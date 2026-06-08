# -*- coding: utf-8 -*-
"""Move Zhou Yi classics from 03梅花易学 to 12周易 under 未入库古籍/1."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "未入库古籍" / "1"
TARGET_CAT = "12周易"
SOURCE_CATS = ("03梅花易学", "10杂占方术")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_chm_guji import classify_book  # noqa: E402


def update_header(text: str, category: str) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines[:8]):
        if line.startswith("分类:"):
            lines[i] = f"分类: {category}"
            break
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    target_dir = OUTPUT / TARGET_CAT
    target_dir.mkdir(parents=True, exist_ok=True)

    moved = 0
    for src_cat in SOURCE_CATS:
        src_dir = OUTPUT / src_cat
        if not src_dir.exists():
            continue
        for path in list(src_dir.glob("*.txt")):
            book_name = path.stem.rsplit("-", 1)[0]
            new_cat = classify_book(book_name, src_cat)
            if new_cat != TARGET_CAT:
                continue
            dest = target_dir / path.name
            text = path.read_text(encoding="utf-8")
            dest.write_text(update_header(text, TARGET_CAT), encoding="utf-8")
            path.unlink()
            print(f"[move] {path.name} -> {TARGET_CAT}/", flush=True)
            moved += 1

    index_path = OUTPUT / "_index.json"
    if index_path.exists():
        stats = json.loads(index_path.read_text(encoding="utf-8"))
        for item in stats:
            book = item["book"]
            if classify_book(book, item["category"]) == TARGET_CAT:
                fname = Path(item["file"]).name
                item["category"] = TARGET_CAT
                item["file"] = str((OUTPUT / TARGET_CAT / fname).relative_to(ROOT))
        index_path.write_text(
            json.dumps(stats, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"\nMoved {moved} books to {TARGET_CAT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
