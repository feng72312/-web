"""Seed ziwei structured nodes into graph/ziwei_nodes.jsonl (run from repo root)."""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[2] / "knowledge" / "data" / "graph" / "ziwei_nodes.jsonl"

PALACES = (
    "命宫",
    "兄弟",
    "夫妻",
    "子女",
    "财帛",
    "疾厄",
    "迁移",
    "奴仆",
    "官禄",
    "田宅",
    "福德",
    "父母",
)

MAJOR_STARS = (
    "紫微",
    "天机",
    "太阳",
    "武曲",
    "天同",
    "廉贞",
    "天府",
    "太阴",
    "贪狼",
    "巨门",
    "天相",
    "天梁",
    "七杀",
    "破军",
)


def main() -> None:
    nodes: list[dict] = []
    for palace in PALACES:
        nodes.append(
            {
                "id": f"ziwei_palace:{palace}",
                "topic": "ziwei_palace",
                "sourceTier": "T2",
                "sourceCategory": "11紫微斗数",
                "sourceFile": "紫微斗数全书-明-陈希夷.txt",
                "lookupKey": {"palaceName": palace},
                "summary": f"紫微{palace}: 宫干宫支与主星组合定该宫人事吉凶.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "ziwei",
            }
        )
    for star in MAJOR_STARS:
        nodes.append(
            {
                "id": f"ziwei_star:{star}",
                "topic": "ziwei_star",
                "sourceTier": "T2",
                "sourceCategory": "11紫微斗数",
                "sourceFile": "紫微斗数全书-明-陈希夷.txt",
                "lookupKey": {"starName": star},
                "summary": f"紫微主星{star}: 入命入身及三方四正时, 参宫干四化与对宫辅星论吉凶.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "ziwei",
            }
        )
    OUTPUT.write_text(
        "\n".join(json.dumps(n, ensure_ascii=False) for n in nodes) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(nodes)} nodes -> {OUTPUT}")


if __name__ == "__main__":
    main()
