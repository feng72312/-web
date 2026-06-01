"""Seed meihua structured nodes into graph/meihua_nodes.jsonl (run from repo root)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.liuyao.hexagram import HEXAGRAM_NAMES  # noqa: E402
from app.core.liuyao.trigrams import PALACE_ELEMENT, TRIGRAM_IDS  # noqa: E402

OUTPUT = ROOT / "knowledge" / "data" / "graph" / "meihua_nodes.jsonl"


def main() -> None:
    nodes: list[dict] = []
    nodes.append(
        {
            "id": "ti_yong:general",
            "topic": "ti_yong",
            "sourceTier": "T1",
            "sourceCategory": "03梅花易学",
            "sourceFile": "梅花易数-宋-邵雍.txt",
            "lookupKey": {"tiGua": "", "yongGua": "", "relation": "general"},
            "summary": "有动爻则动爻所在卦为用、另一卦为体; 无动爻则下卦为体、上卦为用.",
            "claims": [],
            "agreementLevel": "single_source",
            "safeAutoAnswer": False,
            "domain": "meihua",
        }
    )
    for (lower_id, upper_id), name in HEXAGRAM_NAMES.items():
        lower = TRIGRAM_IDS[lower_id]
        upper = TRIGRAM_IDS[upper_id]
        nodes.append(
            {
                "id": f"gua:{name}",
                "topic": "gua",
                "sourceTier": "T1",
                "sourceCategory": "03梅花易学",
                "sourceFile": "梅花易数-宋-邵雍.txt",
                "lookupKey": {"benGuaName": name, "lower": lower, "upper": upper},
                "summary": (
                    f"{name}: 下{lower}({PALACE_ELEMENT[lower]}) "
                    f"上{upper}({PALACE_ELEMENT[upper]})."
                ),
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "meihua",
            }
        )
    OUTPUT.write_text(
        "\n".join(json.dumps(n, ensure_ascii=False) for n in nodes) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(nodes)} nodes -> {OUTPUT}")


if __name__ == "__main__":
    main()
