# -*- coding: utf-8 -*-
"""Build shuowen_entries.json and naming_strokes.json for the naming module."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT.parent / "数据库" / "12实用专区" / "起名"
OUT_DIR = Path(__file__).resolve().parents[1] / "data"
SHUOWEN_TXT = SOURCE_DIR / "01_说文解字_许慎.txt"
MAKEMEAHANZI_URL = (
    "https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt"
)

ENTRY_HEAD = re.compile(r"^【(.+?)】$")
META_LINE = re.compile(r"^部首:\s*(.+?)\s*\|\s*卷:\s*(.+?)\s*\|\s*反切:\s*(.+)$")
VARIANT_LINE = re.compile(r"^\s*重文\s+(.+?):\s*(.+)$")
DUAN_LINE = re.compile(r"^\s*段注(?:\s*\[(.+?)\])?\s*(.+)$")
XUAN_LINE = re.compile(r"^\s*徐(?:铉|锴)注:\s*(.+)$")


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def parse_shuowen(text: str) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    current: dict | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("=") or line.startswith("书名:"):
            continue

        head = ENTRY_HEAD.match(line)
        if head:
            word = head.group(1)
            current = {
                "char": word,
                "radical": "",
                "volume": "",
                "pronunciation": "",
                "explanation": "",
                "variants": [],
                "duanNotes": [],
                "xuanNote": "",
            }
            entries[word] = current
            continue

        if current is None:
            continue

        meta = META_LINE.match(line)
        if meta:
            current["radical"] = meta.group(1).strip()
            current["volume"] = meta.group(2).strip()
            current["pronunciation"] = meta.group(3).strip()
            continue

        variant = VARIANT_LINE.match(line)
        if variant:
            current["variants"].append(
                {"char": variant.group(1).strip(), "note": variant.group(2).strip()}
            )
            continue

        duan = DUAN_LINE.match(line)
        if duan:
            current["duanNotes"].append(
                {"quote": (duan.group(1) or "").strip(), "note": duan.group(2).strip()}
            )
            continue

        xuan = XUAN_LINE.match(line)
        if xuan:
            current["xuanNote"] = xuan.group(1).strip()
            continue

        if line.startswith("段注") or line.startswith("徐"):
            continue

        if not current["explanation"]:
            current["explanation"] = line

    return entries


def fetch_makemeahanzi_strokes() -> dict[str, int]:
    strokes: dict[str, int] = {}
    try:
        with urllib.request.urlopen(MAKEMEAHANZI_URL, timeout=120) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ch = row.get("character")
                stroke_list = row.get("strokes")
                if ch and isinstance(stroke_list, list) and stroke_list:
                    strokes[ch] = len(stroke_list)
    except Exception as exc:
        print(f"[warn] makemeahanzi fetch failed: {exc}")
    return strokes


def merge_stroke_tables(*sources: dict[str, int]) -> dict[str, int]:
    merged: dict[str, int] = {}
    for table in sources:
        merged.update(table)
    return merged


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SHUOWEN_TXT.is_file():
        raise FileNotFoundError(f"missing shuowen source: {SHUOWEN_TXT}")

    text = read_text(SHUOWEN_TXT)
    entries = parse_shuowen(text)
    makemeahanzi = fetch_makemeahanzi_strokes()

    zhuge_path = OUT_DIR / "zhuge_strokes.json"
    zhuge_strokes: dict[str, int] = {}
    if zhuge_path.is_file():
        zhuge_strokes = json.loads(zhuge_path.read_text(encoding="utf-8"))

    strokes = merge_stroke_tables(makemeahanzi, zhuge_strokes)

    shuowen_out = OUT_DIR / "shuowen_entries.json"
    shuowen_out.write_text(
        json.dumps({"entries": entries, "count": len(entries)}, ensure_ascii=False),
        encoding="utf-8",
    )
    strokes_out = OUT_DIR / "naming_strokes.json"
    strokes_out.write_text(
        json.dumps(strokes, ensure_ascii=False),
        encoding="utf-8",
    )

    covered = sum(1 for ch in entries if ch in strokes)
    print(f"shuowen entries: {len(entries)}")
    print(f"stroke table: {len(strokes)} chars ({covered}/{len(entries)} shuowen covered)")


if __name__ == "__main__":
    main()
