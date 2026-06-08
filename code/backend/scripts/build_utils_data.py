# -*- coding: utf-8 -*-
"""Build zhuge_qian.json and jiemeng_entries.json from 数据库/12实用专区."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT.parent / "数据库" / "12实用专区"
OUT_DIR = Path(__file__).resolve().parents[1] / "data"

# Kangxi-style stroke counts for chars in corpus (extend as needed).
STROKE_OVERRIDES: dict[str, int] = {
    "佑": 7,
    "咱": 9,
    "统": 12,
    "林": 8,
    "山": 3,
    "冲": 6,
    "韶": 14,
}


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "gb18030", "gbk"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def parse_zhuge_qian(text: str) -> dict[str, str]:
    lines = text.splitlines()
    start = False
    qian: dict[str, str] = {}
    pattern = re.compile(r"^\s*(\d+)\s*[。.．]\s*(.+)$")
    for line in lines:
        if "查签" in line:
            start = True
            continue
        if not start:
            continue
        m = pattern.match(line.strip())
        if not m:
            continue
        num = int(m.group(1))
        body = re.sub(r"\s+", " ", m.group(2)).strip()
        if body:
            qian[str(num)] = body
    return qian


def parse_jiemeng_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    section = ""
    section_re = re.compile(r"^[一二三四五六七八九十百]+、")
    verdict_markers = ("主", "吉", "凶", "亨", "利", "成", "败", "病", "财", "官")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("诗曰") or line == "周公解梦":
            continue
        if section_re.match(line):
            section = line
            continue
        if len(line) < 6:
            continue
        if not any(m in line for m in verdict_markers):
            continue
        entries.append({"section": section, "text": line, "keyword": line[: min(12, len(line))]})
    return entries


def collect_strokes(texts: list[str]) -> dict[str, int]:
    chars: set[str] = set()
    for text in texts:
        for ch in text:
            if "\u4e00" <= ch <= "\u9fff":
                chars.add(ch)
    strokes: dict[str, int] = {}
    for ch in sorted(chars):
        strokes[ch] = STROKE_OVERRIDES.get(ch, 8)
    return strokes


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zhuge_path = SOURCE_DIR / "秘本诸葛神数-三国蜀-诸葛亮.txt"
    jiemeng_path = SOURCE_DIR / "周公解梦--佚名.txt"

    zhuge_text = read_text(zhuge_path)
    jiemeng_text = read_text(jiemeng_path)

    qian = parse_zhuge_qian(zhuge_text)
    entries = parse_jiemeng_entries(jiemeng_text)
    strokes = collect_strokes([zhuge_text, jiemeng_text, read_text(SOURCE_DIR / "测字秘牒-清-程省.txt")])

    out_qian = OUT_DIR / "zhuge_qian.json"
    if out_qian.exists():
        existing = json.loads(out_qian.read_text(encoding="utf-8")).get("qian", {})
        for key, value in existing.items():
            if int(key) >= 231 and value.strip():
                qian[key] = value
    out_qian.write_text(
        json.dumps({"qian": qian, "maxNo": 384}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "jiemeng_entries.json").write_text(
        json.dumps({"entries": entries}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "zhuge_strokes.json").write_text(
        json.dumps(strokes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"zhuge qian: {len(qian)} entries")
    print(f"jiemeng: {len(entries)} entries")
    print(f"strokes: {len(strokes)} chars")
    print("Run build_naming_data.py separately for shuowen / naming_strokes indexes.")


if __name__ == "__main__":
    main()
