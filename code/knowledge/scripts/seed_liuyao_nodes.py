"""Seed liuyao structured nodes into graph/liuyao_nodes.jsonl (run from repo root)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.liuyao.hexagram import HEXAGRAM_NAMES  # noqa: E402
from app.core.liuyao.trigrams import PALACE_ELEMENT, TRIGRAM_IDS  # noqa: E402

OUTPUT = ROOT / "knowledge" / "data" / "graph" / "liuyao_nodes.jsonl"


def main() -> None:
    nodes: list[dict] = []
    nodes.append(
        {
            "id": "yong_shen:general",
            "topic": "yong_shen",
            "sourceTier": "T2",
            "sourceCategory": "02六爻卜筮",
            "sourceFile": "增删卜易-清-野鹤老人.txt",
            "lookupKey": {"relation": "general"},
            "summary": "六爻占事先定用神: 问财取妻财, 问官取官鬼, 问婚取世应, 再以动爻生克断吉凶.",
            "claims": [],
            "agreementLevel": "single_source",
            "safeAutoAnswer": False,
            "domain": "liuyao",
        }
    )
    for (lower_id, upper_id), name in HEXAGRAM_NAMES.items():
        lower = TRIGRAM_IDS[lower_id]
        upper = TRIGRAM_IDS[upper_id]
        nodes.append(
            {
                "id": f"liuyao_gua:{name}",
                "topic": "gua",
                "sourceTier": "T2",
                "sourceCategory": "02六爻卜筮",
                "sourceFile": "周易-佚名.txt",
                "lookupKey": {"benGuaName": name, "lower": lower, "upper": upper},
                "summary": (
                    f"{name}: 下{lower}({PALACE_ELEMENT[lower]}) "
                    f"上{upper}({PALACE_ELEMENT[upper]}), 六爻纳甲断法见增删卜易."
                ),
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "liuyao",
            }
        )
    OUTPUT.write_text(
        "\n".join(json.dumps(n, ensure_ascii=False) for n in nodes) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(nodes)} nodes -> {OUTPUT}")


if __name__ == "__main__":
    main()
