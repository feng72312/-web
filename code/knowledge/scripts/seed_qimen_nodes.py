"""Seed qimen structured nodes (run from repo root).

  py knowledge/scripts/seed_qimen_nodes.py
  py knowledge/scripts/extract_qimen_from_faqiao.py --merge
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "knowledge" / "data" / "graph" / "qimen_nodes.jsonl"

DOORS = ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
STARS = [
    "天蓬",
    "天芮",
    "天冲",
    "天辅",
    "天禽",
    "天心",
    "天柱",
    "天任",
    "天英",
]
GODS = ["值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天", "白虎", "玄武"]


def main() -> None:
    nodes: list[dict] = []
    nodes.append(
        {
            "id": "ju:chaibu_rule",
            "topic": "ju",
            "sourceTier": "T1",
            "sourceCategory": "04奇门遁甲",
            "sourceFile": "奇门法窍-清-锡孟樨.txt",
            "lookupKey": {"dunType": "", "juNumber": "", "yuan": "", "jieqi": ""},
            "summary": "时家奇门拆补定局: 依节气三元与符头定阴阳遁与局数, 转盘排天盘八门九星八神.",
            "claims": [],
            "agreementLevel": "single_source",
            "safeAutoAnswer": False,
            "domain": "qimen",
        }
    )
    for dun, nums in (("阳遁", "一二三四五六七八九"), ("阴遁", "一二三四五六七八九")):
        for ch in nums:
            num = "一二三四五六七八九".index(ch) + 1
            for yuan in ("上元", "中元", "下元"):
                nodes.append(
                    {
                        "id": f"ju:{dun}{num}{yuan}",
                        "topic": "ju",
                        "sourceTier": "T2",
                        "sourceCategory": "04奇门遁甲",
                        "sourceFile": "奇门法窍-清-锡孟樨.txt",
                        "lookupKey": {
                            "dunType": dun,
                            "juNumber": str(num),
                            "yuan": yuan,
                            "jieqi": "",
                        },
                        "summary": f"{dun}{ch}局{yuan}: 依节气符头所定之局.",
                        "claims": [],
                        "agreementLevel": "single_source",
                        "safeAutoAnswer": False,
                        "domain": "qimen",
                    }
                )
    for door in DOORS:
        nodes.append(
            {
                "id": f"men:{door}",
                "topic": "men",
                "sourceTier": "T2",
                "sourceCategory": "04奇门遁甲",
                "sourceFile": "奇门法窍-清-锡孟樨.txt",
                "lookupKey": {"door": door},
                "summary": f"{door}: 八门之一, 主事之出入与吉凶趋势.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "qimen",
            }
        )
    for star in STARS:
        nodes.append(
            {
                "id": f"xing:{star}",
                "topic": "xing",
                "sourceTier": "T2",
                "sourceCategory": "04奇门遁甲",
                "sourceFile": "奇门法窍-清-锡孟樨.txt",
                "lookupKey": {"star": star},
                "summary": f"{star}: 九星之一, 主天时与态势.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "qimen",
            }
        )
    for god in GODS:
        nodes.append(
            {
                "id": f"shen:{god}",
                "topic": "shen",
                "sourceTier": "T2",
                "sourceCategory": "04奇门遁甲",
                "sourceFile": "奇门法窍-清-锡孟樨.txt",
                "lookupKey": {"god": god},
                "summary": f"{god}: 八神之一, 主神煞与辅助象意.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "qimen",
            }
        )
    for cat, label in (("shizhan", "事占"), ("xingzhan", "行占")):
        nodes.append(
            {
                "id": f"yong:{cat}",
                "topic": "yong",
                "sourceTier": "T2",
                "sourceCategory": "04奇门遁甲",
                "sourceFile": "奇门法窍-清-锡孟樨.txt",
                "lookupKey": {"category": cat},
                "summary": f"{label}: 用神取法须合问事类别与方位, 值符值使与门星神并参.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "qimen",
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
