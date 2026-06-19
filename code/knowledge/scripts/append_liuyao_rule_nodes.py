"""Append executable liuyao rule nodes to graph/liuyao_nodes.jsonl."""

from __future__ import annotations

import json
import sys
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = KNOWLEDGE_DIR / "data" / "graph" / "liuyao_nodes.jsonl"

BASE_META = {
    "sourceCategory": "02六爻卜筮",
    "claims": [],
    "agreementLevel": "single_source",
    "safeAutoAnswer": False,
    "domain": "liuyao",
    "authorityTier": "S",
}


def _node(
    node_id: str,
    topic: str,
    summary: str,
    *,
    classic: str,
    source_file: str,
    lookup_key: dict,
    source_tier: str = "T1",
    evidence_role: str = "core_divination_judge",
    conditions: dict | None = None,
) -> dict:
    row = {
        "id": node_id,
        "topic": topic,
        "sourceTier": source_tier,
        "sourceFile": source_file,
        "lookupKey": lookup_key,
        "summary": summary,
        "classic": classic,
        **BASE_META,
        "evidenceRole": evidence_role,
    }
    if conditions:
        row["conditions"] = conditions
    return row


def build_rule_nodes() -> list[dict]:
    nodes: list[dict] = []

    topic_specs = [
        ("wealth", "妻财", "问财求财以妻财为用神"),
        ("career", "官鬼", "问官仕途以官鬼为用神"),
        ("exam", "父母", "考试文书以父母为用神"),
        ("marriage", "妻财", "男占婚姻以妻财为用神, 兼看世应"),
        ("self_illness", "世爻", "自占疾病以世爻为用神"),
        ("illness", "官鬼", "占病以官鬼为病, 子孙为医"),
        ("parents", "父母", "占父母以父母爻为用神"),
        ("siblings", "兄弟", "占兄弟以兄弟爻为用神"),
        ("children", "子孙", "占子孙孕产以子孙为用神"),
        ("lawsuit", "官鬼", "官非诉讼以官鬼为用神"),
        ("travel", "世爻", "出行以世爻为用神"),
        ("lost_item", "妻财", "失物以妻财为用神"),
        ("weather", "父母", "天气以父母为用神"),
        ("house", "父母", "田宅以父母为用神"),
        ("friend", "应爻", "问朋友外人以应爻为用神"),
    ]
    for topic_id, ys, summary in topic_specs:
        nodes.append(
            _node(
                f"liuyao:topic:{topic_id}:yong_shen",
                "yong_shen",
                summary,
                classic="增删卜易",
                source_file="S_主裁经典/增删卜易--野鹤老人.txt",
                lookup_key={"topicId": topic_id, "yongShen": ys},
                conditions={"topicId": topic_id},
            )
        )

    wang_shuai_rules = [
        ("yue_jian_sheng", "用神得月建生扶为旺"),
        ("yue_jian_ke", "用神受月建克制为衰"),
        ("ri_chen_sheng", "用神得日辰生扶有力"),
        ("ri_chen_ke", "用神受日辰克制为弱"),
        ("dong_sheng", "动爻生用神为吉"),
        ("dong_ke", "动爻克用神为凶"),
        ("hui_tou_sheng", "变爻回头生用神为吉"),
        ("hui_tou_ke", "变爻回头克用神为凶"),
    ]
    for key, summary in wang_shuai_rules:
        nodes.append(
            _node(
                f"liuyao:wang_shuai:{key}",
                "wang_shuai",
                summary,
                classic="增删卜易",
                source_file="S_主裁经典/增删卜易--野鹤老人.txt",
                lookup_key={"rule": key},
            )
        )

    liu_chong_rules = [
        ("near_illness", "近病逢六冲可不药而愈"),
        ("chronic_illness", "久病逢六冲难愈"),
        ("near_plan", "近谋逢六冲事散"),
        ("lawsuit_escape", "避讼逢六冲宜散"),
        ("general", "六冲主散, 须分占事"),
    ]
    for key, summary in liu_chong_rules:
        nodes.append(
            _node(
                f"liuyao:dong_bian:liu_chong:{key}",
                "dong_bian",
                summary,
                classic="增删卜易",
                source_file="S_主裁经典/增删卜易--野鹤老人.txt",
                lookup_key={"pattern": "liu_chong", "scope": key},
            )
        )

    bian_rules = [
        ("xun_kong", "旬空", "用神旬空事难成, 待填实可验"),
        ("yue_po", "月破", "用神月破力量弱, 待补破可转机"),
        ("fei_fu", "飞伏", "用神不上卦须查伏神"),
        ("fan_yin", "反吟", "动爻反吟主反复"),
        ("fu_yin", "伏吟", "伏吟主呻吟不进"),
        ("jin_tui", "进退", "化进神应速, 化退神应迟"),
    ]
    for key, label, summary in bian_rules:
        topic = "xun_kong" if key == "xun_kong" else "yue_po" if key == "yue_po" else "fei_fu" if key == "fei_fu" else "dong_bian"
        nodes.append(
            _node(
                f"liuyao:{topic}:{key}",
                topic,
                f"{label}: {summary}",
                classic="卜筮正宗",
                source_file="S_主裁经典/卜筮正宗-清-王洪绪.txt",
                lookup_key={"rule": key},
            )
        )

    yingqi_rules = [
        ("he_yong_shen", "合用神之日月为应期"),
        ("chong_yong_shen", "冲用神之日月为应期"),
        ("dong_yao", "动爻化出之期"),
        ("kong_shi", "旬空填实之期"),
        ("po_shi", "月破补破之期"),
    ]
    for key, summary in yingqi_rules:
        nodes.append(
            _node(
                f"liuyao:ying_qi:{key}",
                "ying_qi",
                summary,
                classic="增删卜易",
                source_file="S_主裁经典/增删卜易--野鹤老人.txt",
                lookup_key={"rule": key},
            )
        )

    huang_topics = [
        ("wealth_topic", "求财", "求财专论"),
        ("career_topic", "功名", "功名官禄专论"),
        ("marriage_topic", "婚姻", "婚姻专论"),
        ("illness_topic", "疾病", "疾病专论"),
        ("travel_topic", "出行", "出行专论"),
        ("lawsuit_topic", "官非", "官非专论"),
        ("weather_topic", "天气", "晴雨专论"),
        ("lost_topic", "失物", "失物专论"),
        ("house_topic", "宅运", "田宅专论"),
        ("child_topic", "子嗣", "子嗣专论"),
    ]
    for key, label, summary in huang_topics:
        nodes.append(
            _node(
                f"liuyao:topic_divination:{key}",
                "topic_divination",
                summary,
                classic="黄金策",
                source_file="S_主裁经典/黄金策-明-刘基.txt",
                lookup_key={"topic": label},
                evidence_role="classic_topic_judge",
            )
        )

    shi_ying_rules = [
        ("shi_self", "世爻代表占者本人"),
        ("ying_other", "应爻代表对方事体"),
        ("shi_ying_sheng", "世应相生事易成"),
        ("shi_ying_ke", "世应相克事多阻"),
        ("shi_empty", "世爻旬空占者心意不定"),
        ("ying_empty", "应爻旬空对方无力"),
    ]
    for key, summary in shi_ying_rules:
        nodes.append(
            _node(
                f"liuyao:shi_ying:{key}",
                "shi_ying",
                summary,
                classic="卜筮正宗",
                source_file="S_主裁经典/卜筮正宗-清-王洪绪.txt",
                lookup_key={"rule": key},
            )
        )

    return nodes


def main() -> int:
    existing: list[dict] = []
    if OUTPUT.is_file():
        for line in OUTPUT.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if str(row.get("topic")) == "gua":
                existing.append(row)
            elif str(row.get("id")) == "yong_shen:general":
                continue

    rule_nodes = build_rule_nodes()
    merged = existing + rule_nodes
    OUTPUT.write_text(
        "\n".join(json.dumps(n, ensure_ascii=False) for n in merged) + "\n",
        encoding="utf-8",
    )
    rule_count = len(rule_nodes)
    gua_count = len(existing)
    print(
        json.dumps(
            {
                "ruleNodes": rule_count,
                "guaNodes": gua_count,
                "total": len(merged),
                "output": str(OUTPUT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if rule_count >= 55 else 2

if __name__ == "__main__":
    sys.exit(main())
