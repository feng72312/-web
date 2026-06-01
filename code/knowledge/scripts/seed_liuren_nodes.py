"""Seed liuren structured nodes (run from repo root).

  py knowledge/scripts/seed_liuren_nodes.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "knowledge" / "data" / "graph" / "liuren_nodes.jsonl"

YUE_JIANG = [
    "亥",
    "戌",
    "酉",
    "申",
    "未",
    "午",
    "巳",
    "辰",
    "卯",
    "寅",
    "丑",
    "子",
]
GENERALS = [
    "贵人",
    "螣蛇",
    "朱雀",
    "六合",
    "勾陈",
    "青龙",
    "天空",
    "白虎",
    "太常",
    "玄武",
    "太阴",
    "天后",
]


def main() -> None:
    nodes: list[dict] = []
    for zhi in YUE_JIANG:
        nodes.append(
            {
                "id": f"yue_jiang:{zhi}",
                "topic": "yue_jiang",
                "sourceTier": "T2",
                "sourceCategory": "05大六壬",
                "sourceFile": "六壬指南.txt",
                "lookupKey": {"yueJiang": zhi},
                "summary": f"月将{zhi}: 占时月将加时起天地盘.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "liuren",
            }
        )
    for gen in GENERALS:
        nodes.append(
            {
                "id": f"tian_jiang:{gen}",
                "topic": "tian_jiang",
                "sourceTier": "T2",
                "sourceCategory": "05大六壬",
                "sourceFile": "六壬指南.txt",
                "lookupKey": {"general": gen},
                "summary": f"天将{gen}: 三传四课所乘之神.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "liuren",
            }
        )
    for cat in ("shizhan", "xingzhan"):
        nodes.append(
            {
                "id": f"yong:{cat}",
                "topic": "yong",
                "sourceTier": "T2",
                "sourceCategory": "05大六壬",
                "sourceFile": "六壬指南.txt",
                "lookupKey": {"category": cat},
                "summary": (
                    "事占用神: 以日干为体, 支上神为用."
                    if cat == "shizhan"
                    else "行占用神: 以行年、驿马、天马参断."
                ),
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "liuren",
            }
        )
    nodes.append(
        {
            "id": "jinkou:rule",
            "topic": "jinkou",
            "sourceTier": "T1",
            "sourceCategory": "05大六壬",
            "sourceFile": "金口诀古本.txt",
            "lookupKey": {"renYuan": "", "difen": ""},
            "summary": "金口诀: 以人元、贵神、将神、地分四字断事.",
            "claims": [],
            "agreementLevel": "single_source",
            "safeAutoAnswer": False,
            "domain": "liuren",
        }
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as fh:
        for node in nodes:
            fh.write(json.dumps(node, ensure_ascii=False) + "\n")
    print(f"wrote {len(nodes)} nodes -> {OUTPUT}")


if __name__ == "__main__":
    main()
