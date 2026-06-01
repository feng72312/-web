#!/usr/bin/env python
"""Seed structured dayun (大运) rule nodes from 命理探源 excerpts."""

from __future__ import annotations

import json
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "dayun_tanyuan.draft.jsonl"
SOURCE_FILE = "命理探源--袁树珊.txt"
SOURCE_CATEGORY = "01八字命理"


def _claim(quote: str, conclusion: str, chapter: str) -> dict:
    return {
        "classic": "命理探源",
        "edition": "袁树珊",
        "chapter": chapter,
        "quote": quote,
        "conclusion": conclusion,
        "role": "primary",
        "aligns": None,
        "sourceFile": SOURCE_FILE,
        "sourceCategory": SOURCE_CATEGORY,
    }


def build_nodes() -> list[dict]:
    rules: list[tuple[str, str, str]] = [
        (
            "core",
            "大运如地, 太岁如人. 十年一运, 须先看命局用神喜忌, 再论运支是否得地、运干是否助用. 换运之年多主吉凶转折.",
            "日主为身, 局神为舟马, 大运为地, 太岁为人.",
        ),
        (
            "xingyun_xiji",
            "行运喜忌: 用神在运中得生扶则顺, 忌神当权则逆. 运克用神如舟失顺风; 运助用神如危局得援. 须与流年联看.",
            "运来克用神, 如舟行风逆; 运助用神, 如顺风扬帆.",
        ),
        (
            "gan_zhi_weight",
            "大运重地支(行运之地), 天干为表象. 运支冲命局用神之支, 该运多逆; 运支合用神之支, 该运多顺.",
            "大运重地支, 太岁重天干.",
        ),
        (
            "start_rule",
            "起运以节气与顺逆为准, 童限小运可补大运不足. 题干虚龄须换算公历再对大运表.",
            "小运补大运, 须先定八字喜忌.",
        ),
        (
            "dayun_change",
            "交运前后一年常主环境、职业或家庭结构变动. 换运时应结合前后两运喜忌对比.",
            "交脱大运, 吉凶易显.",
        ),
        (
            "suiyun_note",
            "大运与流年并看: 运吉岁凶或运凶岁吉, 以用神得失与冲合轻重权衡.",
            "太岁一至, 休咎即显.",
        ),
    ]
    nodes: list[dict] = []
    for category, summary, quote in rules:
        nodes.append(
            {
                "id": f"dayun:{category}",
                "topic": "dayun",
                "sourceTier": "T1",
                "sourceCategory": SOURCE_CATEGORY,
                "sourceFile": SOURCE_FILE,
                "lookupKey": {"category": category},
                "summary": summary,
                "claims": [_claim(quote, summary, "论大运")],
                "agreementLevel": "single_source",
                "safeAutoAnswer": False,
                "domain": "bazi",
                "reviewedAt": None,
            }
        )
    return nodes


def main() -> None:
    nodes = build_nodes()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as fh:
        for node in nodes:
            fh.write(json.dumps(node, ensure_ascii=False) + "\n")
    print(f"wrote {len(nodes)} nodes -> {OUTPUT}")


if __name__ == "__main__":
    main()
