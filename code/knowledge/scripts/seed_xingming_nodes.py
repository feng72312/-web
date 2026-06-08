"""Seed xingming structured nodes (run from repo root).

  py code/knowledge/scripts/seed_xingming_nodes.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "graph" / "xingming_nodes.jsonl"

SI_YU = [
    ("rahu", "\u7f57\u55e3"),
    ("ketu", "\u8ba1\u90fd"),
    ("yuebei", "\u6708\u5b5a"),
    ("ziqi", "\u7d2b\u6c14"),
]
SEVEN = [
    ("sun", "\u65e5"),
    ("moon", "\u6708"),
    ("mercury", "\u6c34"),
    ("venus", "\u91d1"),
    ("mars", "\u706b"),
    ("jupiter", "\u6728"),
    ("saturn", "\u571f"),
]
PALACES = [
    "\u547d\u5bab",
    "\u8d22\u535a",
    "\u5144\u5f1f",
    "\u7530\u5b85",
    "\u7537\u5973",
    "\u5974\u4ec6",
    "\u592b\u59bb",
    "\u75be\u5384",
    "\u8fc1\u79fb",
    "\u5b98\u7984",
    "\u798f\u5fb7",
    "\u76f8\u8c8c",
]


def main() -> None:
    nodes: list[dict] = []
    for sid, label in SEVEN + SI_YU:
        nodes.append(
            {
                "id": f"shou_ming:{sid}",
                "topic": "shou_ming",
                "sourceTier": "T2",
                "sourceCategory": "09\u661f\u547d\u5360\u9a8c",
                "sourceFile": "\u661f\u5b66\u5927\u6210-\u660e-\u4e07\u6c11\u82f1.txt",
                "lookupKey": {"starId": sid},
                "summary": f"{label}\u5b88\u547d: \u53c2\u89c1\u661f\u5b66\u5927\u6210\u4e03\u653f\u56db\u4f59\u65ad\u8bed.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "xingming",
            }
        )
    for name in PALACES:
        nodes.append(
            {
                "id": f"palace:{name}",
                "topic": "palace",
                "sourceTier": "T2",
                "sourceCategory": "09\u661f\u547d\u5360\u9a8c",
                "sourceFile": "\u661f\u5b66\u5927\u6210-\u660e-\u4e07\u6c11\u82f1.txt",
                "lookupKey": {"palaceName": name},
                "summary": f"{name}\u4e3b\u4e8b\u9879\u4e0e\u751f\u514b.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "xingming",
            }
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "\n".join(json.dumps(n, ensure_ascii=False) for n in nodes) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(nodes)} nodes -> {OUTPUT}")


if __name__ == "__main__":
    main()
