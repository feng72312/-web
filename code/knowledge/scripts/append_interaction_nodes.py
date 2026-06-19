"""Write interactions topic nodes into draft JSONL for compile_graph."""

from __future__ import annotations

import json
import sys
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = KNOWLEDGE_DIR / "data" / "draft" / "interactions_core.draft.jsonl"

NODES = [
    {
        "id": "interactions:pattern:stem_he",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
        "lookupKey": {"pattern": "stem_he", "category": "pillar_interaction"},
        "summary": "天干五合可化气或羁绊, 须看合化条件与格局喜忌. 合而不化多主牵绊、迟滞, 不可单以合论吉.",
        "claims": [
            {
                "classic": "子平真诠",
                "edition": "沈孝瞻",
                "chapter": "论合",
                "quote": "合而有情则吉, 合而无情或争合则滞.",
                "conclusion": "天干五合须辨化与不化, 合化成功则气势转移; 合而不化则干支羁绊, 作辅助判断.",
                "role": "primary",
                "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:branch_chong",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
        "lookupKey": {"pattern": "branch_chong", "category": "pillar_interaction"},
        "summary": "地支六冲主动荡、拆变、对立. 冲月令或冲用神之支, 格局与六亲易有波折; 冲去忌神亦可成救应.",
        "claims": [
            {
                "classic": "子平真诠",
                "edition": "沈孝瞻",
                "chapter": "论正官",
                "quote": "以刑冲破害为忌, 则以生之护之为喜矣.",
                "conclusion": "地支相冲须结合格局成败与用神喜忌, 冲忌神为解, 冲喜神为破.",
                "role": "primary",
                "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:branch_he",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "滴天髓阐微-清-任铁樵.txt",
        "lookupKey": {"pattern": "branch_he", "category": "pillar_interaction"},
        "summary": "地支六合多主和合、牵制、转化. 合住用神则滞, 合去忌神则顺; 须与冲害并看, 不可单论.",
        "claims": [
            {
                "classic": "滴天髓",
                "edition": "任铁樵",
                "chapter": "合局",
                "quote": "合而有情则吉, 合而争战则凶.",
                "conclusion": "地支相合要辨有情无情, 合化与合绊不同, 须参格局与岁运.",
                "role": "primary",
                "sourceFile": "滴天髓阐微-清-任铁樵.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:branch_hai",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "神峰通考-明-张楠.txt",
        "lookupKey": {"pattern": "branch_hai", "category": "pillar_interaction"},
        "summary": "六害多主暗伤、猜忌、阻滞. 害日支或月令, 感情与身体宜慎; 与冲并见则动荡加重.",
        "claims": [
            {
                "classic": "神峰通考",
                "edition": "张楠",
                "chapter": "论刑冲会合",
                "quote": "害者, 暗中损伤, 不可不察.",
                "conclusion": "六害为暗动, 须结合十神宫位与流年大运, 作辅助断语.",
                "role": "primary",
                "sourceFile": "神峰通考-明-张楠.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:branch_xing",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "神峰通考-明-张楠.txt",
        "lookupKey": {"pattern": "branch_xing", "category": "pillar_interaction"},
        "summary": "地支相刑多主是非、官非、伤病、六亲不和. 三刑全见动荡尤甚; 须回归十神与格局, 不可单以刑断凶.",
        "claims": [
            {
                "classic": "神峰通考",
                "edition": "张楠",
                "chapter": "论刑冲会合",
                "quote": "刑者, 刑罚伤灾, 须察其由何十神引发.",
                "conclusion": "相刑为明伤, 与冲害并看; 刑去忌神或成局者另论.",
                "role": "primary",
                "sourceFile": "神峰通考-明-张楠.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:branch_po",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "渊海子平-宋-徐升.txt",
        "lookupKey": {"pattern": "branch_po", "category": "pillar_interaction"},
        "summary": "相破多主内部耗损、关系裂痕、计划中断. 破月令或用神之支, 事业与身体易有反复.",
        "claims": [
            {
                "classic": "渊海子平",
                "edition": "徐升",
                "chapter": "论破",
                "quote": "破则散, 散则难聚, 须看破何神何宫.",
                "conclusion": "地支相破为细伤, 与冲刑并见则加重; 作辅助象.",
                "role": "primary",
                "sourceFile": "渊海子平-宋-徐升.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "A",
    },
    {
        "id": "interactions:pattern:sanhe",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "滴天髓阐微-清-任铁樵.txt",
        "lookupKey": {"pattern": "sanhe", "category": "pillar_interaction"},
        "summary": "三合局成则气势专一, 可助格局或夺月令之气. 须辨化神是否得令得地, 以及是否破坏原有用神.",
        "claims": [
            {
                "classic": "滴天髓",
                "edition": "任铁樵",
                "chapter": "合局",
                "quote": "三合成局, 其气专一, 可成可败, 全在化神之得令与否.",
                "conclusion": "三合局须结合月令与透干, 不可单以合局论富贵.",
                "role": "primary",
                "sourceFile": "滴天髓阐微-清-任铁樵.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:sanhui",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "滴天髓阐微-清-任铁樵.txt",
        "lookupKey": {"pattern": "sanhui", "category": "pillar_interaction"},
        "summary": "三会方局气聚一方, 旺衰偏枯明显. 与格局体用冲突时, 须以调候与格局成败先断.",
        "claims": [
            {
                "classic": "滴天髓",
                "edition": "任铁樵",
                "chapter": "方局",
                "quote": "三会其气尤专, 偏旺偏枯, 不可不辨.",
                "conclusion": "三会方局为气势变化, 辅助格局与调候判断.",
                "role": "primary",
                "sourceFile": "滴天髓阐微-清-任铁樵.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:half_he",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
        "lookupKey": {"pattern": "half_he", "category": "pillar_interaction"},
        "summary": "半合为合局未成, 多主牵制、待时应期. 半合用神则迟滞, 半合忌神则略有解.",
        "claims": [
            {
                "classic": "子平真诠",
                "edition": "沈孝瞻",
                "chapter": "论合",
                "quote": "合中有半, 半合待引, 引动则发.",
                "conclusion": "半合须待大运流年补全, 作应期与辅助判断.",
                "role": "primary",
                "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:punish_triple",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "神峰通考-明-张楠.txt",
        "lookupKey": {"pattern": "punish_triple", "category": "pillar_interaction"},
        "summary": "寅巳申三刑、丑戌未三刑全见, 动荡与官非伤病信息增强. 须看何神被刑及是否刑去忌神.",
        "claims": [
            {
                "classic": "神峰通考",
                "edition": "张楠",
                "chapter": "论刑冲会合",
                "quote": "三刑全见, 其象愈烈, 不可不察.",
                "conclusion": "三刑组须结合十神与流年大运, 不得单论大凶.",
                "role": "primary",
                "sourceFile": "神峰通考-明-张楠.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:day_pillar_focus",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
        "lookupKey": {"pattern": "day_pillar_focus", "category": "pillar_interaction"},
        "summary": "日支为夫妻宫, 日支逢冲合害刑, 婚姻感情与配偶状况易有引动. 须与配偶星、流年并看.",
        "claims": [
            {
                "classic": "子平真诠",
                "edition": "沈孝瞻",
                "chapter": "论婚姻",
                "quote": "日支动则配偶宫动, 冲合刑害皆主婚姻有变.",
                "conclusion": "日支作用为婚姻感情辅助象, 不得越权定格局.",
                "role": "primary",
                "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:month_pillar_focus",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
        "lookupKey": {"pattern": "month_pillar_focus", "category": "pillar_interaction"},
        "summary": "月令为提纲, 月支逢冲合刑害, 格局体用与事业根基易有波动. 冲提纲尤须慎断.",
        "claims": [
            {
                "classic": "子平真诠",
                "edition": "沈孝瞻",
                "chapter": "论月令",
                "quote": "月令一动, 格局随之而变, 冲之则根摇.",
                "conclusion": "月支作用须回归格局成败, 辅助调候与岁运.",
                "role": "primary",
                "sourceFile": "子平真诠评注-清-沈孝瞻.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:stem_clash",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "渊海子平-宋-徐升.txt",
        "lookupKey": {"pattern": "stem_clash", "category": "pillar_interaction"},
        "summary": "天干相克或相冲并见, 多主表面冲突、竞争、压力. 须看是否为用神受制或忌神相战.",
        "claims": [
            {
                "classic": "渊海子平",
                "edition": "徐升",
                "chapter": "论天干",
                "quote": "天干相克, 其象在事, 须辨克谁为谁用.",
                "conclusion": "天干冲克为浅层作用, 辅助十神与格局判断.",
                "role": "primary",
                "sourceFile": "渊海子平-宋-徐升.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "A",
    },
    {
        "id": "interactions:pattern:zheng_he",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "滴天髓阐微-清-任铁樵.txt",
        "lookupKey": {"pattern": "zheng_he", "category": "pillar_interaction"},
        "summary": "争合、妒合多主感情纠葛、资源争夺、迟滞。须辨合化真假与格局喜忌.",
        "claims": [
            {
                "classic": "滴天髓",
                "edition": "任铁樵",
                "chapter": "合局",
                "quote": "争合则乱, 妒合则滞.",
                "conclusion": "争合为合之变异, 辅助婚姻与财运判断.",
                "role": "primary",
                "sourceFile": "滴天髓阐微-清-任铁樵.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "S",
    },
    {
        "id": "interactions:pattern:shensha",
        "topic": "interactions",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "神峰通考-明-张楠.txt",
        "lookupKey": {"pattern": "shensha", "category": "pillar_interaction"},
        "summary": "神煞为辅助象, 不可夺格局与用神之正. 桃花、驿马、羊刃等须回归十神与冲合会害统看.",
        "claims": [
            {
                "classic": "神峰通考",
                "edition": "张楠",
                "chapter": "论神煞",
                "quote": "神煞不可执一, 须以格局用神为主.",
                "conclusion": "神煞仅作象义补充, 不得压过月令格局与调候用神.",
                "role": "primary",
                "sourceFile": "神峰通考-明-张楠.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
        "evidenceRole": "interactions_judge",
        "authorityTier": "A",
    },
]


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as fh:
        for node in NODES:
            fh.write(json.dumps(node, ensure_ascii=False) + "\n")
    print(f"wrote {len(NODES)} interaction nodes -> {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
