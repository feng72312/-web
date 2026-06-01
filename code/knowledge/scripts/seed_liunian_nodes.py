#!/usr/bin/env python
"""Seed structured liunian (流年) rule nodes from 命理探源 / 三命通会 excerpts."""

from __future__ import annotations

import json
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "liunian_tanyuan.draft.jsonl"
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
    # One node per category; lookupKey.category is the index field.
    rules: list[tuple[str, str, str]] = [
        (
            "core",
            "流年为逐年太岁, 主一年祸福. 须先看日主强弱与用神喜忌, 再论太岁与四柱、大运生克冲合. 太岁如君, 大运如臣, 和悦则吉, 战斗则凶.",
            "《三命通会》: 流年者逐年游行之太岁, 主一年祸福, 不可不细察.",
        ),
        (
            "taisui_relation",
            "岁伤日主(太岁克日主)祸较轻; 日犯岁君(日主克太岁)灾较重. 日主克太岁而局中有制化或合化可减凶甚至反财; 四柱无情则克岁难解.",
            "岁伤日主有祸必轻; 日犯岁君见灾必重. 五行有救其年反必为财, 四柱无情故论克岁.",
        ),
        (
            "zhen_taisui",
            "流年干支同日主日柱为真太岁; 须与大运用神协和方吉, 遇刑冲破害则凶. 日柱与流年天克地冲多主凶祸.",
            "甲子日逢甲子流年为真太岁; 癸巳日丁亥流年冲克太岁亦凶.",
        ),
        (
            "suiyun_binglin",
            "流年与大运干支相同为岁运并临. 羊刃七煞多凶, 财官印绶多吉.",
            "甲子流年逢甲子大运为岁运并临; 经云岁运并临灾殃立至指羊刃七煞.",
        ),
        (
            "dayun_synergy",
            "大运重地支为行运之地, 太岁重天干为所遇之年. 须权喜忌: 用神得岁运扶助则顺, 冲克用神则逆.",
            "日主为身, 局神为舟马, 大运为地, 太岁为人. 太岁一至休咎即显.",
        ),
        (
            "zhan_chong_he",
            "运克岁为运伐岁, 岁克运为岁伐岁, 看日主喜忌. 运冲岁、岁冲岁须看党众轻重. 乙庚、子丑等可论和气.",
            "战冲和好: 丙运庚年, 子运午年, 午运子年, 须结合喜忌.",
        ),
        (
            "yongshen_timing",
            "局中缺用神而岁运补上, 如危局得助; 用神被岁运冲克, 如舟断顺风. 须结合大运再看流年.",
            "甲春局无金, 岁运得金土可补; 局有金用神而岁运无助则难.",
        ),
        (
            "xiaoyun_note",
            "小运补大运不足; 须先定八字喜忌再与大运比较. 命宫主一生, 小限主一年.",
            "小运行死绝煞旺多危难, 长生临官多安宁.",
        ),
        (
            "push_method",
            "以当年流年干支论十神生克, 须合大运、四柱, 不可单看流年一字. 题干有虚龄须先换算公历流年.",
            "凡推流年以本流年干支为主; 结合大运小限与四柱.",
        ),
        (
            "event_guanfei",
            "流年官杀旺或七杀攻身, 再遇冲刑, 多主官非、牢狱、口舌纠纷; 须看用神是否有救.",
            "七杀无制, 流年冲克, 主官非伤灾.",
        ),
        (
            "event_health",
            "流年冲克用神或印星, 多主疾病手术; 伤官见官、枭印夺食等组合须结合大运.",
            "用神受伤, 岁运冲刑, 主疾.",
        ),
        (
            "event_marriage",
            "流年财星或配偶星引动, 合动婚姻宫(日支), 多主婚恋变化; 比劫夺财则不利.",
            "财星逢合, 日支逢冲, 婚姻易动.",
        ),
        (
            "event_wealth",
            "流年财星得用则进财, 比劫分财或财星入墓则破耗; 须合大运喜忌.",
            "财为养命之源, 岁运生扶则丰.",
        ),
        (
            "event_career",
            "流年官杀或食伤变动, 多主工作、创业、职位变化; 官印相生则升职.",
            "官星得用, 主事业进展.",
        ),
        (
            "event_family",
            "流年印星或偏财引动, 多主父母、长辈、家庭变故; 印星受克则忧母.",
            "印绶逢冲, 长辈有忧.",
        ),
    ]
    nodes: list[dict] = []
    for category, summary, quote in rules:
        nodes.append(
            {
                "id": f"liunian:{category}",
                "topic": "liunian",
                "sourceTier": "T1",
                "sourceCategory": SOURCE_CATEGORY,
                "sourceFile": SOURCE_FILE,
                "lookupKey": {"category": category},
                "summary": summary,
                "claims": [_claim(quote, summary, "论流年")],
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
