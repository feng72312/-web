"""Extract tiaohou nodes from 穷通宝鉴 txt into draft JSONL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
DEFAULT_SOURCE = ROOT / "数据库" / "01八字命理" / "穷通宝鉴-明-余春台.txt"
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "tiaohou_qiongtong.draft.jsonl"

DAY_GANS = list("甲乙丙丁戊己庚辛壬癸")
MONTH_LABELS = [
    "正月",
    "二月",
    "三月",
    "四月",
    "五月",
    "六月",
    "七月",
    "八月",
    "九月",
    "十月",
    "十一月",
    "十二月",
]
LABEL_TO_ZHI = {
    "正月": "寅",
    "二月": "卯",
    "三月": "辰",
    "四月": "巳",
    "五月": "午",
    "六月": "未",
    "七月": "申",
    "八月": "酉",
    "九月": "戌",
    "十月": "亥",
    "十一月": "子",
    "十二月": "丑",
}

SECTION_RE = re.compile(r"^三([春夏秋冬])([甲乙丙丁戊己庚辛壬癸])")
ENTRY_RE = re.compile(
    r"^(正月|二月|三月|四月|五月|六月|七月|八月|九月|十月|十一月|十二月)"
    r"([甲乙丙丁戊己庚辛壬癸])"
)


def _trim_summary(text: str, limit: int = 120) -> str:
    cleaned = re.sub(r"\s+", "", text)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "..."


def read_source_text(path: Path) -> str:
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def extract(source_path: Path) -> list[dict]:
    raw = read_source_text(source_path)
    source_file = "穷通宝鉴-明-余春台.txt"
    nodes: list[dict] = []
    current_chapter = ""
    current_gan = ""
    current_season = ""
    buffer: list[str] = []
    buffer_key: tuple[str, str] | None = None

    def flush() -> None:
        nonlocal buffer, buffer_key
        if not buffer_key or not buffer:
            buffer = []
            buffer_key = None
            return
        month_label, day_gan = buffer_key
        month_zhi = LABEL_TO_ZHI[month_label]
        quote = "".join(buffer).strip()
        if len(quote) < 8:
            buffer = []
            buffer_key = None
            return
        node_id = f"tiaohou:{day_gan}:{month_zhi}"
        chapter = current_chapter or f"{current_season}{day_gan} / {month_label}{day_gan}"
        nodes.append(
            {
                "id": node_id,
                "topic": "tiaohou",
                "sourceTier": "T1",
                "sourceCategory": "01八字命理",
                "sourceFile": source_file,
                "lookupKey": {
                    "dayGan": day_gan,
                    "monthZhi": month_zhi,
                    "monthLabel": month_label,
                },
                "summary": _trim_summary(quote),
                "claims": [
                    {
                        "classic": "穷通宝鉴",
                        "edition": "余春台",
                        "chapter": chapter,
                        "quote": quote[:500],
                        "conclusion": _trim_summary(quote, 80),
                        "role": "primary",
                        "aligns": None,
                        "sourceFile": source_file,
                        "sourceCategory": "01八字命理",
                    }
                ],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "bazi",
                "reviewedAt": None,
            }
        )
        buffer = []
        buffer_key = None

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        section_match = SECTION_RE.match(line)
        if section_match:
            flush()
            current_season = f"三{section_match.group(1)}"
            current_gan = section_match.group(2)
            current_chapter = line
            continue
        if line.endswith("总论") and len(line) <= 12:
            current_chapter = line
            continue

        entry_match = ENTRY_RE.match(line)
        if entry_match:
            flush()
            month_label = entry_match.group(1)
            day_gan = entry_match.group(2)
            if day_gan != current_gan and current_gan:
                current_chapter = f"{current_season}{day_gan} / {month_label}{day_gan}"
            buffer_key = (month_label, day_gan)
            rest = line[entry_match.end() :].lstrip("，, ")
            buffer = [rest] if rest else []
            continue

        if buffer_key is not None:
            buffer.append(line)

    flush()

    # dedupe by id, keep longest quote
    merged: dict[str, dict] = {}
    for node in nodes:
        node_id = node["id"]
        if node_id not in merged:
            merged[node_id] = node
            continue
        if len(node["claims"][0]["quote"]) > len(merged[node_id]["claims"][0]["quote"]):
            merged[node_id] = node
    return list(merged.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args()
    source = Path(args.source)
    if not source.exists():
        print(f"source not found: {source}")
        return 1

    nodes = extract(source)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for node in nodes:
            fh.write(json.dumps(node, ensure_ascii=False) + "\n")
    print(f"extracted {len(nodes)} nodes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
