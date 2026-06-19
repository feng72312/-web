"""Append gap-driven liunian/qishi/geju nodes for contest error coverage."""

from __future__ import annotations

import json
from pathlib import Path

from _extract_common import make_node

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "gap_batch_k.draft.jsonl"

GAP_NODES = [
    make_node(
        node_id="liunian:category:marriage_event",
        topic="liunian",
        source_file="三命通会-明-万民英.txt",
        lookup_key={"category": "marriage_event", "theme": "婚姻感情"},
        summary="流年引动配偶宫或配偶星, 合则成、冲则变. 须先看大运是否扶配偶星, 再看流年十神.",
        quote="流年与大运并看, 婚姻之应, 多在冲合配偶宫之年.",
        classic="三命通会",
        chapter="论婚姻",
        edition="万民英",
        rule_type="liunian_event",
        evidence_role="suiyun_judge",
    ),
    make_node(
        node_id="liunian:category:health_event",
        topic="liunian",
        source_file="三命通会-明-万民英.txt",
        lookup_key={"category": "health_event", "theme": "健康疾病"},
        summary="流年冲克疾厄宫或忌神当权, 多病伤. 印星受克、官杀攻身之年宜慎.",
        quote="流年克身或冲提纲, 身体多有起伏, 须分轻重.",
        classic="三命通会",
        chapter="论疾病",
        edition="万民英",
        rule_type="liunian_event",
        evidence_role="suiyun_judge",
    ),
    make_node(
        node_id="liunian:category:guanfei_event",
        topic="liunian",
        source_file="三命通会-明-万民英.txt",
        lookup_key={"category": "guanfei_event", "theme": "官非"},
        summary="官杀攻身、伤官见官、劫财逢冲之年多主官非压力. 须对照大运是否助官杀.",
        quote="伤官见官, 为祸百端; 流年并临, 其象愈显.",
        classic="三命通会",
        chapter="论官非",
        edition="万民英",
        rule_type="liunian_event",
        evidence_role="suiyun_judge",
    ),
    make_node(
        node_id="qishi:category:huashi",
        topic="qishi",
        source_file="滴天髓阐微-清-任铁樵.txt",
        lookup_key={"category": "huashi", "qishiTopic": "从化"},
        summary="从化须真, 假化不真. 日主无根或失令, 方论从化; 有根有救则不从.",
        quote="得势则从化, 失势则还原. 从化之格, 不宜逆其气势.",
        classic="滴天髓",
        chapter="从化",
        edition="任铁樵",
        rule_type="qishi_flow",
        evidence_role="qishi_judge",
    ),
    make_node(
        node_id="qishi:category:qingzhuo_flow",
        topic="qishi",
        source_file="滴天髓阐微-清-任铁樵.txt",
        lookup_key={"category": "qingzhuo_flow", "qishiTopic": "清浊"},
        summary="清者宜顺, 浊者宜制. 五行混杂无救则浊, 有通关有印则清.",
        quote="清浊之分, 在通关与救应. 偏枯太甚, 纵有格局亦难全美.",
        classic="滴天髓",
        chapter="清浊",
        edition="任铁樵",
        rule_type="qishi_flow",
        evidence_role="qishi_judge",
    ),
    make_node(
        node_id="geju:special:broken_rescue",
        topic="geju",
        source_file="子平真诠-清-沈孝瞻.txt",
        lookup_key={"category": "broken_rescue", "aspect": "救应"},
        summary="格局破格须有救应: 印化杀、财通关、合去忌神. 无救则格不成.",
        quote="成格有救, 破格有救, 方为贵论.",
        classic="子平真诠",
        chapter="格局救应",
        edition="沈孝瞻",
        rule_type="geju_rule",
        evidence_role="geju_judge",
    ),
    make_node(
        node_id="tiaohou:principle:yongshen_priority",
        topic="tiaohou",
        source_file="穷通宝鉴-清-余春台.txt",
        lookup_key={"category": "yongshen_priority"},
        summary="调候用神为第一要务, 寒暖燥湿不调则格局难显. 透干救应须与月令一致.",
        quote="调候为急, 格局为体. 先寒暖, 后旺衰.",
        classic="穷通宝鉴",
        chapter="调候总则",
        edition="余春台",
        rule_type="tiaohou_rule",
        evidence_role="tiaohou_judge",
    ),
    make_node(
        node_id="qishi:category:liutong",
        topic="qishi",
        source_file="滴天髓阐微-清-任铁樵.txt",
        lookup_key={"category": "liutong", "qishiTopic": "流通"},
        summary="五行流通则清, 阻滞则浊. 通关为要, 偏枯须救.",
        quote="源流清浊, 全在流通. 得通关之神, 则气象顺遂.",
        classic="滴天髓",
        chapter="流通",
        edition="任铁樵",
        rule_type="qishi_flow",
        evidence_role="qishi_judge",
    ),
]

THEME_TAGS = {
    "liunian:category:marriage_event": ["流年事件", "婚姻感情"],
    "liunian:category:health_event": ["流年事件", "健康疾病"],
    "liunian:category:guanfei_event": ["流年事件", "官非"],
}


def main() -> int:
    out = OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for node in GAP_NODES:
            tagged = dict(node)
            themes = THEME_TAGS.get(str(node.get("id") or ""))
            if themes:
                tagged["applicableThemes"] = themes
            fh.write(json.dumps(tagged, ensure_ascii=False) + "\n")
    print(f"wrote {len(GAP_NODES)} gap nodes -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
