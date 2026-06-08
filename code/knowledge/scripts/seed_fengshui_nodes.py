"""Seed feng shui structured nodes (run from repo root).

  py knowledge/scripts/seed_fengshui_nodes.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "knowledge" / "data" / "graph" / "fengshui_nodes.jsonl"

MOUNTAINS = [
    ("ren", "壬", "坎"),
    ("zi", "子", "坎"),
    ("gui", "癸", "坎"),
    ("chou", "丑", "艮"),
    ("gen", "艮", "艮"),
    ("yin", "寅", "艮"),
    ("jia", "甲", "震"),
    ("mao", "卯", "震"),
    ("yi", "乙", "震"),
    ("chen", "辰", "巽"),
    ("xun", "巽", "巽"),
    ("si", "巳", "巽"),
    ("bing", "丙", "离"),
    ("wu", "午", "离"),
    ("ding", "丁", "离"),
    ("wei", "未", "坤"),
    ("kun", "坤", "坤"),
    ("shen", "申", "坤"),
    ("geng", "庚", "兑"),
    ("you", "酉", "兑"),
    ("xin", "辛", "兑"),
    ("xu", "戌", "乾"),
    ("qian", "乾", "乾"),
    ("hai", "亥", "乾"),
]

TRIGRAMS = [
    ("1", "坎", "北", "dongsi"),
    ("2", "坤", "西南", "xisi"),
    ("3", "震", "东", "dongsi"),
    ("4", "巽", "东南", "dongsi"),
    ("6", "乾", "西北", "xisi"),
    ("7", "兑", "西", "xisi"),
    ("8", "艮", "东北", "xisi"),
    ("9", "离", "南", "dongsi"),
]

JI_XIONG = [
    ("fuWei", "伏位", True),
    ("shengQi", "生气", True),
    ("yanNian", "延年", True),
    ("tianYi", "天医", True),
    ("jueMing", "绝命", False),
    ("wuGui", "五鬼", False),
    ("liuSha", "六煞", False),
    ("huoHai", "祸害", False),
]

STARS = [
    ("1", "一白贪狼", "水"),
    ("2", "二黑巨门", "土"),
    ("3", "三碧禄存", "木"),
    ("4", "四绿文曲", "木"),
    ("5", "五黄廉贞", "土"),
    ("6", "六白武曲", "金"),
    ("7", "七赤破军", "金"),
    ("8", "八白左辅", "土"),
    ("9", "九紫右弼", "火"),
]

PERIODS = [
    ("1", "1864", "1883", "上元"),
    ("2", "1884", "1903", "上元"),
    ("3", "1904", "1923", "上元"),
    ("4", "1924", "1943", "中元"),
    ("5", "1944", "1963", "中元"),
    ("6", "1964", "1983", "中元"),
    ("7", "1984", "2003", "下元"),
    ("8", "2004", "2023", "下元"),
    ("9", "2024", "2043", "下元"),
]


def main() -> None:
    nodes: list[dict] = []
    for mid, name, trigram in MOUNTAINS:
        nodes.append(
            {
                "id": f"shan:{mid}",
                "topic": "shan",
                "sourceTier": "T2",
                "sourceCategory": "06风水堪舆",
                "sourceFile": "二十四山八卦罗经图.txt",
                "lookupKey": {"mountainId": mid, "mountain": name},
                "summary": f"{name}山属{trigram}卦, 为玄空下卦与八宅坐向之基本单元.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "fengshui",
            }
        )
    for num, name, direction, group in TRIGRAMS:
        label = "东四" if group == "dongsi" else "西四"
        nodes.append(
            {
                "id": f"ming_gua:{num}",
                "topic": "ming_gua",
                "sourceTier": "T2",
                "sourceCategory": "06风水堪舆",
                "sourceFile": "阳宅指南-明-蒋大鸿.txt",
                "lookupKey": {"guaNumber": num, "guaName": name},
                "summary": f"{name}卦({direction}), {label}命/宅常用卦位.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "fengshui",
            }
        )
    for key, label, auspicious in JI_XIONG:
        nodes.append(
            {
                "id": f"ji_xiong_fang:{key}",
                "topic": "ji_xiong_fang",
                "sourceTier": "T2",
                "sourceCategory": "06风水堪舆",
                "sourceFile": "阳宅指南-明-蒋大鸿.txt",
                "lookupKey": {"type": key, "label": label},
                "summary": f"八宅{label}方, {'吉方' if auspicious else '凶方'}, 用于门床灶布局.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "fengshui",
            }
        )
    for num, name, element in STARS:
        nodes.append(
            {
                "id": f"star:{num}",
                "topic": "star",
                "sourceTier": "T2",
                "sourceCategory": "06风水堪舆",
                "sourceFile": "沈氏玄空学.txt",
                "lookupKey": {"starNumber": num},
                "summary": f"{name}星, 五行属{element}, 玄空飞星基本星体.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "fengshui",
            }
        )
    for num, start, end, yuan in PERIODS:
        nodes.append(
            {
                "id": f"period:{num}",
                "topic": "period",
                "sourceTier": "T1",
                "sourceCategory": "06风水堪舆",
                "sourceFile": "沈氏玄空学.txt",
                "lookupKey": {"period": num},
                "summary": f"{num}运({start}-{end}), {yuan}, 玄空当运之星入中.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "fengshui",
            }
        )
    for scene, label in (("residence", "住宅"), ("shop", "店铺"), ("office", "办公室")):
        nodes.append(
            {
                "id": f"scene:{scene}",
                "topic": "scene",
                "sourceTier": "T2",
                "sourceCategory": "06风水堪舆",
                "sourceFile": "阳宅指南-明-蒋大鸿.txt",
                "lookupKey": {"scene": scene},
                "summary": f"{label}阳宅布局, 门主灶室为要.",
                "claims": [],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "fengshui",
            }
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "\n".join(json.dumps(node, ensure_ascii=False) for node in nodes) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(nodes)} nodes -> {OUTPUT}")


if __name__ == "__main__":
    main()
