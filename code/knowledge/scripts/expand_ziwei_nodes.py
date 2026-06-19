"""Expand ziwei_nodes.jsonl to >= 100 executable rule nodes."""

from __future__ import annotations

import json
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = KNOWLEDGE_DIR / "data" / "graph" / "ziwei_nodes.jsonl"

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

PATTERNS = (
    ("sha_po_lang", "杀破狼", {"stars": ["七杀", "破军", "贪狼"]}),
    ("fu_xiang", "府相朝垣", {"stars": ["天府", "天相"]}),
    ("ji_yue_tong_liang", "机月同梁", {"stars": ["天机", "太阴", "天同", "天梁"]}),
    ("ri_yue", "日月并明", {"stars": ["太阳", "太阴"]}),
    ("zi_fu", "紫府同宫", {"stars": ["紫微", "天府"]}),
    ("lian_tan", "廉贞贪狼", {"stars": ["廉贞", "贪狼"]}),
    ("wu_tan", "武曲贪狼", {"stars": ["武曲", "贪狼"]}),
    ("tian_ji_yue", "天机太阴", {"stars": ["天机", "太阴"]}),
    ("yang_tuo", "阳梁昌禄", {"stars": ["太阳", "天梁"]}),
    ("sha_ji", "杀忌同宫", {"stars": ["七杀"]}),
    ("po_jun_zhan", "破军独坐", {"stars": ["破军"]}),
    ("zi_wei_wang", "紫微独旺", {"stars": ["紫微"]}),
)

MUTAGEN_TYPES = ("禄", "权", "科", "忌")
MUTAGEN_SOURCES = ("命宫", "夫妻", "财帛", "官禄", "迁移", "福德", "疾厄")


def _base_node(**overrides) -> dict:
    row = {
        "sourceTier": "T2",
        "sourceCategory": "11紫微斗数",
        "sourceFile": "S_核心法本/《太微賦》精解.txt",
        "claims": [],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "ziwei",
        "school": "general",
        "authorityTier": "S",
    }
    row.update(overrides)
    return row


def load_existing() -> list[dict]:
    if not OUTPUT.is_file():
        return []
    rows: list[dict] = []
    for line in OUTPUT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def build_new_nodes(existing_ids: set[str]) -> list[dict]:
    nodes: list[dict] = []

    for palace in PALACES:
        node_id = f"ziwei_palace_topic:{palace}"
        if node_id in existing_ids:
            continue
        nodes.append(
            _base_node(
                id=node_id,
                topic="ziwei_palace_topic",
                lookupKey={"palaceName": palace, "category": "theme"},
                summary=f"{palace}宫主题: 仅在该宫人事边界内辅助, 须合三方四正与对宫.",
                conditions={"palaceScope": [palace], "requiresTriad": True},
                libraryRole="topic_library",
                evidenceRole="palace_topic_support",
            )
        )

    for star in MAJOR_STARS:
        for brightness in ("庙旺", "平", "陷弱"):
            node_id = f"ziwei_star_brightness:{star}:{brightness}"
            if node_id in existing_ids:
                continue
            nodes.append(
                _base_node(
                    id=node_id,
                    topic="ziwei_star",
                    lookupKey={"starName": star, "brightnessBand": brightness},
                    summary=f"主星{star}在{brightness}时, 须合落宫与三方四正, 不得单星定论.",
                    conditions={"starName": star, "brightnessBand": brightness},
                    sourceFile="A_星曜格局/紫微命理之细论星情.txt",
                    authorityTier="A",
                    evidenceRole="star_judge",
                )
            )

    for pattern_id, label, cond in PATTERNS:
        node_id = f"ziwei_pattern:{pattern_id}"
        if node_id in existing_ids:
            continue
        nodes.append(
            _base_node(
                id=node_id,
                topic="ziwei_pattern",
                lookupKey={"patternName": label},
                summary=f"格局{label}: 须校验{','.join(cond['stars'])}位置与三方四正, 破格则降置信度.",
                conditions={"requiredStars": cond["stars"], "checkPalaces": ["命宫", "迁移", "财帛", "官禄"]},
                sourceFile="A_星曜格局/紫微格局研究.txt",
                authorityTier="A",
                evidenceRole="pattern_judge",
            )
        )

    for source in MUTAGEN_SOURCES:
        for mutagen in MUTAGEN_TYPES:
            node_id = f"ziwei_mutagen:{source}:{mutagen}"
            if node_id in existing_ids:
                continue
            nodes.append(
                _base_node(
                    id=node_id,
                    topic="ziwei_mutagen",
                    lookupKey={"fromPalace": source, "mutagenType": mutagen},
                    summary=f"{source}化{mutagen}飞星: 须给出来源宫、落宫、冲照宫与scope.",
                    conditions={"fromPalace": source, "mutagenType": mutagen, "requiresDirection": True},
                    school="feixing",
                    evidenceRole="mutagen_judge",
                )
            )

    for school in ("sanhe", "feixing"):
        node_id = f"ziwei_cross_school:{school}"
        if node_id in existing_ids:
            continue
        nodes.append(
            _base_node(
                id=node_id,
                topic="ziwei_cross_school",
                lookupKey={"school": school},
                summary=f"法派{school}主裁权重: 另一派仅作schoolCommentary辅助.",
                conditions={"primarySchool": school},
                school=school,
            )
        )

    for palace in PALACES:
        node_id = f"ziwei_limit:{palace}"
        if node_id in existing_ids:
            continue
        nodes.append(
            _base_node(
                id=node_id,
                topic="ziwei_limit",
                lookupKey={"palaceName": palace, "scope": "decadal_yearly"},
                summary=f"限运引动{palace}时, 须分层合参本命{palace}与三方四正.",
                conditions={"triggerPalace": palace},
                evidenceRole="limit_judge",
            )
        )

    return nodes


def main() -> int:
    existing = load_existing()
    existing_ids = {str(row.get("id") or "") for row in existing}
    new_nodes = build_new_nodes(existing_ids)
    merged = existing + new_nodes
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in merged) + "\n",
        encoding="utf-8",
    )
    executable = sum(1 for row in merged if not row.get("safeAutoAnswer"))
    print(f"nodes_total={len(merged)} new={len(new_nodes)} executable={executable}")
    return 0 if executable >= 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())
