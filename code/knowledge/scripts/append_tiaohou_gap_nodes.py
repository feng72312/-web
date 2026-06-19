"""Append missing tiaohou nodes for val benchmark dayGan:monthZhi gaps."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
DRAFT_PATH = KNOWLEDGE_DIR / "data" / "draft" / "tiaohou_gap_val.draft.jsonl"
SOURCE_FILE = "穷通宝鉴-明-余春台.txt"

GAP_NODES = [
    {
        "id": "tiaohou:己:申",
        "lookupKey": {"dayGan": "己", "monthZhi": "申", "monthLabel": "七月"},
        "chapter": "三秋己土 / 七月申月",
        "quote": (
            "三秋己土，万物收藏之际，外虚内实，寒气渐升，须丙火温之，癸水润之。"
            "癸能泄金，丙能制金，补土精神，则秋生之物咸茂矣，癸先丙後。"
            "丙癸两透，雁塔题名；支成金局，癸透有根，富中取贵。"
            "总之三秋己土，先癸後丙，取辛辅癸，余皆酌用。"
        ),
    },
    {
        "id": "tiaohou:己:戌",
        "lookupKey": {"dayGan": "己", "monthZhi": "戌", "monthLabel": "九月"},
        "chapter": "三秋己土 / 九月戌月",
        "quote": (
            "三秋己土，万物收藏之际，外虚内实，寒气渐升，须丙火温之，癸水润之，癸先丙後。"
            "九月土盛，宜甲木疏之，余皆酌用。"
            "丙透癸藏，遇金颇有选援；八月支成金局，得丙透丁藏，生己元神，名魁天下。"
        ),
    },
    {
        "id": "tiaohou:戊:丑",
        "lookupKey": {"dayGan": "戊", "monthZhi": "丑", "monthLabel": "十二月"},
        "chapter": "冬月之土 / 三冬戊土",
        "quote": (
            "冬月之土，外寒内温，水旺才丰，金多子秀，火盛有荣，木无咎，再加比肩扶助为佳。"
            "三冬己土，非丙暖不生，取丙为尊，甲木参酌；初冬壬旺，取戊制之，余皆用丙丁。"
            "凡三冬土，见壬水出干，须戊土制之或丙火温之，方不为水浸寒泥。"
        ),
    },
    {
        "id": "tiaohou:丁:酉",
        "lookupKey": {"dayGan": "丁", "monthZhi": "酉", "monthLabel": "八月"},
        "chapter": "三秋丁火 / 八九月丁火",
        "quote": (
            "八九月丁火：一派辛金，不见庚金，又无比劫，比弃命从财，富而且贵。"
            "或九月一派戊土，泄丁火之气，不见甲木，为伤官伤尽，非寻常可比；"
            "或甲木透出，为文书清贵，秋闱可夺，用甲者，庚不可少，水妻木子。"
            "七八月或无甲木，乙亦可用，为枯草引灯，却不离丙晒也。"
        ),
    },
    {
        "id": "tiaohou:乙:丑",
        "lookupKey": {"dayGan": "乙", "monthZhi": "丑", "monthLabel": "十二月"},
        "chapter": "三冬乙木 / 十二月丑月",
        "quote": (
            "十一月乙木，花木寒冻，一阳来复，喜用丙火解冻，则花木有向阳之意，不宜用癸以冻花木，端用丙火。"
            "冬月之木，虽取戊制水，不可作用，端取丙火则可。用火者，木妻、火子。"
            "乙木生于冬月，己土透干，又有丙透，大富贵之造；无丙，一介寒儒。"
        ),
    },
]


def _trim(text: str, limit: int = 120) -> str:
    cleaned = text.replace("\n", "").replace(" ", "")
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1] + "..."


def build_nodes() -> list[dict]:
    nodes: list[dict] = []
    for spec in GAP_NODES:
        quote = spec["quote"]
        nodes.append(
            {
                "id": spec["id"],
                "topic": "tiaohou",
                "sourceTier": "T1",
                "sourceCategory": "01八字命理",
                "sourceFile": SOURCE_FILE,
                "lookupKey": spec["lookupKey"],
                "summary": _trim(quote),
                "claims": [
                    {
                        "classic": "穷通宝鉴",
                        "edition": "余春台",
                        "chapter": spec["chapter"],
                        "quote": quote,
                        "conclusion": _trim(quote, 80),
                        "role": "primary",
                        "aligns": None,
                        "sourceFile": SOURCE_FILE,
                        "sourceCategory": "01八字命理",
                    }
                ],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "bazi",
                "reviewedAt": None,
                "evidenceRole": "tiaohou_judge",
                "authorityTier": "S",
            }
        )
    return nodes


def main() -> int:
    nodes = build_nodes()
    DRAFT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DRAFT_PATH.open("w", encoding="utf-8") as fh:
        for row in nodes:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(nodes)} gap nodes -> {DRAFT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
