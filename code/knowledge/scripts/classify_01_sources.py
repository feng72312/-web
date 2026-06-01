"""Classify all files under 01八字命理 by source tier T1-T4."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
SOURCE_01 = ROOT / "数据库" / "01八字命理"
OUTPUT = KNOWLEDGE_DIR / "data" / "sources" / "01_index.json"

T1_PATTERNS = (
    "穷通宝鉴",
    "渊海子平",
    "子平真诠",
    "滴天髓",
    "三命通会",
    "五行精纪",
    "神峰通考",
    "珞琭子",
    "李虚中命书",
    "兰台妙选",
    "三命指迷赋",
    "人伦大统赋",
    "乾元秘旨",
    "命理正宗",
    "月谈赋",
)

T2_PATTERNS = ("评注", "阐微", "补注", "千里命稿", "命理探源", "永乐百问")

T3_PATTERNS = (
    "命例",
    "详批",
    "答疑",
    "伤病残灾",
    "全部命例",
    "添情命理解读",
)

T4_PATTERNS = (
    "讲义",
    "技巧",
    "如何读",
    "如何鉴别",
    "特训班",
    "论八字【",
    "虚拟宝库",
    "曲炜-我是",
)


def classify_file(name: str) -> str:
    for pattern in T4_PATTERNS:
        if pattern in name:
            return "T4"
    for pattern in T3_PATTERNS:
        if pattern in name:
            return "T3"
    for pattern in T2_PATTERNS:
        if pattern in name:
            return "T2"
    for pattern in T1_PATTERNS:
        if pattern in name:
            return "T1"
    if "曲炜" in name or "曲伟" in name:
        return "T3"
    if name.endswith((".txt", ".doc", ".docx")):
        return "T2"
    return "T4"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(SOURCE_01))
    args = parser.parse_args()
    source = Path(args.source)
    if not source.exists():
        print(f"source not found: {source}")
        return 1

    files: list[dict] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".txt", ".doc", ".docx"}:
            continue
        rel = str(path.relative_to(ROOT / "数据库"))
        tier = classify_file(path.name)
        files.append(
            {
                "sourceCategory": "01八字命理",
                "sourceFile": rel.replace("\\", "/").split("/", 1)[1]
                if rel.startswith("01")
                else path.name,
                "relativePath": str(path.relative_to(ROOT / "数据库")).replace("\\", "/"),
                "tier": tier,
                "topicsAttempted": [],
            }
        )

    # normalize sourceFile to be relative to category folder
    normalized: list[dict] = []
    for item in files:
        rel_path = item["relativePath"]
        if rel_path.startswith("01八字命理/"):
            source_file = rel_path[len("01八字命理/") :]
        else:
            source_file = rel_path
        normalized.append(
            {
                "sourceCategory": "01八字命理",
                "sourceFile": source_file,
                "tier": item["tier"],
                "topicsAttempted": item["topicsAttempted"],
            }
        )

    payload = {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "filesTotal": len(normalized),
        "byTier": {},
        "files": normalized,
    }
    for tier in ("T1", "T2", "T3", "T4"):
        payload["byTier"][tier] = sum(1 for f in normalized if f["tier"] == tier)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
