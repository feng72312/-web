# -*- coding: utf-8 -*-
"""Fetch tarot public-domain sources and build deck/spreads JSON + RAG txt."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "数据库" / "13塔罗占卜"
DECK_DIR = ROOT / "code" / "backend" / "app" / "core" / "tarot" / "data"
IMAGE_DIR = ROOT / "code" / "frontend" / "public" / "tarot" / "rws"

EKELEN_URL = "https://raw.githubusercontent.com/ekelen/tarot-api/master/static/card_data.json"
LAB_URL = "https://raw.githubusercontent.com/look-fate/tarot-lab/main/TarotDB/cards.json"
RWS_IMAGE_BASE = "https://www.sacred-texts.com/tarot/xr"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TarotBookFetcher/1.0",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
REQUEST_DELAY = 1.5
MAX_RETRIES = 3

SUIT_PREFIX = {"wa": "wands", "cu": "cups", "sw": "swords", "pe": "pentacles"}
COURT_RANK = {"ac": "ace", "02": "2", "03": "3", "04": "4", "05": "5", "06": "6", "07": "7", "08": "8", "09": "9", "10": "10", "pa": "page", "kn": "knight", "qu": "queen", "ki": "king"}

MAJOR_ZH = {
    "The Fool": "愚者",
    "The Magician": "魔术师",
    "The High Priestess": "女祭司",
    "The Empress": "皇后",
    "The Emperor": "皇帝",
    "The Hierophant": "教皇",
    "The Lovers": "恋人",
    "The Chariot": "战车",
    "Fortitude": "力量",
    "Strength": "力量",
    "The Hermit": "隐士",
    "Wheel Of Fortune": "命运之轮",
    "The Wheel of Fortune": "命运之轮",
    "Justice": "正义",
    "The Hanged Man": "倒吊人",
    "Death": "死神",
    "Temperance": "节制",
    "The Devil": "恶魔",
    "The Tower": "塔",
    "The Star": "星星",
    "The Moon": "月亮",
    "The Sun": "太阳",
    "The Last Judgment": "审判",
    "Judgement": "审判",
    "The World": "世界",
}


def fetch_url(url: str, timeout: int = 120) -> str | bytes:
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            if "application/json" in resp.headers.get("Content-Type", "") or url.endswith(".json"):
                return resp.content
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text
        except Exception as exc:
            last_exc = exc
            print(f"    retry {attempt}/{MAX_RETRIES}: {exc}")
            time.sleep(REQUEST_DELAY * attempt)
    raise last_exc  # type: ignore[misc]


def card_id_from_short(name_short: str, name_en: str) -> tuple[str, str | None, int | None, str | None]:
    if name_short.startswith("ar"):
        num = int(name_short[2:])
        return f"major-{num:02d}", None, num, None
    prefix = name_short[:2]
    suffix = name_short[2:]
    suit = SUIT_PREFIX.get(prefix)
    if not suit:
        raise ValueError(f"unknown suit prefix: {name_short}")
    rank = COURT_RANK.get(suffix, suffix)
    if rank.isdigit():
        return f"{suit}-{rank}", suit, int(rank), rank
    return f"{suit}-{rank}", suit, None, rank


def image_path(card_id: str, deck: str) -> str | None:
    if deck == "thoth":
        return None
    if deck == "marseille":
        return f"marseille/{card_id}.jpg"
    return f"rws/{card_id}.jpg"


def split_lab_name(name: str) -> tuple[str, str]:
    for index, char in enumerate(name):
        if "\u4e00" <= char <= "\u9fff":
            en = name[:index].strip()
            zh = name[index:].strip()
            return en or name, zh or name
    return name, name


def build_lab_index(lab_cards: list[dict]) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for item in lab_cards:
        en_name, zh_name = split_lab_name((item.get("name") or "").strip())
        if en_name:
            index[en_name.lower()] = {**item, "nameEn": en_name, "nameZh": zh_name}
    return index


MAJOR_COMMONS: dict[int, str] = {
    0: "RWS_Tarot_00_Fool.jpg",
    1: "RWS_Tarot_01_Magician.jpg",
    2: "RWS_Tarot_02_High_Priestess.jpg",
    3: "RWS_Tarot_03_Empress.jpg",
    4: "RWS_Tarot_04_Emperor.jpg",
    5: "RWS_Tarot_05_Hierophant.jpg",
    6: "RWS_Tarot_06_Lovers.jpg",
    7: "RWS_Tarot_07_Chariot.jpg",
    8: "RWS_Tarot_08_Strength.jpg",
    9: "RWS_Tarot_09_Hermit.jpg",
    10: "RWS_Tarot_10_Wheel_of_Fortune.jpg",
    11: "RWS_Tarot_11_Justice.jpg",
    12: "RWS_Tarot_12_Hanged_Man.jpg",
    13: "RWS_Tarot_13_Death.jpg",
    14: "RWS_Tarot_14_Temperance.jpg",
    15: "RWS_Tarot_15_Devil.jpg",
    16: "RWS_Tarot_16_Tower.jpg",
    17: "RWS_Tarot_17_Star.jpg",
    18: "RWS_Tarot_18_Moon.jpg",
    19: "RWS_Tarot_19_Sun.jpg",
    20: "RWS_Tarot_20_Judgement.jpg",
    21: "RWS_Tarot_21_World.jpg",
}

MINOR_SUIT_PREFIX = {
    "wands": "Wands",
    "cups": "Cups",
    "swords": "Swords",
    "pentacles": "Pents",
}

MINOR_RANK_NUM = {
    "ace": "01",
    "2": "02",
    "3": "03",
    "4": "04",
    "5": "05",
    "6": "06",
    "7": "07",
    "8": "08",
    "9": "09",
    "10": "10",
    "page": "11",
    "knight": "12",
    "queen": "13",
    "king": "14",
}


def commons_filename(card_id: str, arcana: str, suit: str | None, number, rank_suffix: str | None) -> str:
    if arcana == "major":
        major_num = int(card_id.split("-")[1])
        return MAJOR_COMMONS.get(major_num, "")
    if not suit:
        return ""
    rank_key = rank_suffix or (str(number) if isinstance(number, int) else "ace")
    prefix = MINOR_SUIT_PREFIX.get(suit, "")
    rank_num = MINOR_RANK_NUM.get(rank_key, "01")
    return f"{prefix}{rank_num}.jpg"


def build_rws_cards(ekelen: dict, lab_cards: list[dict]) -> list[dict]:
    lab_index = build_lab_index(lab_cards)
    cards: list[dict] = []
    for raw in ekelen.get("cards", []):
        name_en = raw["name"]
        card_id, suit, number, rank_suffix = card_id_from_short(raw["name_short"], name_en)
        lab = lab_index.get(name_en.lower())
        name_zh = (
            (lab or {}).get("nameZh")
            or MAJOR_ZH.get(name_en)
            or name_en
        )
        upright_zh = (lab or {}).get("normal") or MAJOR_ZH.get(name_en, "")
        reversed_zh = (lab or {}).get("reversed") or ""
        if not re.search(r"[\u4e00-\u9fff]", upright_zh):
            upright_zh = (lab or {}).get("normal") or upright_zh
        keywords = re.findall(r"[\u4e00-\u9fff]{2,4}", str((lab or {}).get("normal") or ""))[:5]
        arcana = "major" if raw["type"] == "major" else "minor"
        if arcana == "major":
            major_num = raw.get("value_int")
            if major_num is None:
                raw_val = str(raw.get("value") or "0")
                major_num = 0 if raw_val.upper() == "ZERO" else int(raw_val)
        else:
            major_num = None
        cards.append(
            {
                "id": card_id,
                "arcana": arcana,
                "suit": suit,
                "number": number if arcana == "minor" else major_num,
                "nameEn": name_en,
                "nameZh": name_zh,
                "uprightEn": raw.get("meaning_up", ""),
                "reversedEn": raw.get("meaning_rev", ""),
                "uprightZh": (lab or {}).get("normal") or upright_zh,
                "reversedZh": (lab or {}).get("reversed") or reversed_zh,
                "keywordsZh": keywords,
                "descriptionEn": raw.get("desc", ""),
                "commonsFile": commons_filename(card_id, arcana, suit, number, rank_suffix),
                "image": image_path(card_id, "rws"),
            }
        )
    return cards


def clone_deck(base_cards: list[dict], deck: str, name_zh: str) -> list[dict]:
    cloned: list[dict] = []
    for card in base_cards:
        item = dict(card)
        item["image"] = image_path(card["id"], deck)
        if deck != "rws":
            item["meaningSource"] = "rws-baseline"
        cloned.append(item)
    return cloned


def build_spreads() -> dict:
    return {
        "spreads": [
            {
                "id": "single",
                "nameZh": "单牌占卜",
                "cardCount": 1,
                "complexity": "beginner",
                "questionTypes": ["general", "daily"],
                "positions": [{"index": 1, "labelZh": "神谕", "meaningZh": "对问题的直接指引"}],
            },
            {
                "id": "three-card",
                "nameZh": "三牌阵",
                "cardCount": 3,
                "complexity": "beginner",
                "questionTypes": ["general", "timeline"],
                "positions": [
                    {"index": 1, "labelZh": "过去", "meaningZh": "事情的起因与背景"},
                    {"index": 2, "labelZh": "现在", "meaningZh": "当前状态与核心矛盾"},
                    {"index": 3, "labelZh": "未来", "meaningZh": "发展趋势与可能结果"},
                ],
            },
            {
                "id": "situation-action-outcome",
                "nameZh": "情境-行动-结果",
                "cardCount": 3,
                "complexity": "beginner",
                "questionTypes": ["decision", "action"],
                "positions": [
                    {"index": 1, "labelZh": "情境", "meaningZh": "你面对的处境"},
                    {"index": 2, "labelZh": "行动", "meaningZh": "建议采取的态度或行动"},
                    {"index": 3, "labelZh": "结果", "meaningZh": "若按指引行动的可能走向"},
                ],
            },
            {
                "id": "celtic-cross",
                "nameZh": "凯尔特十字",
                "cardCount": 10,
                "complexity": "advanced",
                "questionTypes": ["general", "life-path", "decision"],
                "positions": [
                    {"index": 1, "labelZh": "现状", "meaningZh": "问事的核心现状"},
                    {"index": 2, "labelZh": "挑战", "meaningZh": "横亘眼前的阻力或助力"},
                    {"index": 3, "labelZh": "潜意识", "meaningZh": "深层动机或隐藏因素"},
                    {"index": 4, "labelZh": "过去", "meaningZh": "已发生的关键影响"},
                    {"index": 5, "labelZh": "意识", "meaningZh": "你 conscious 的目标与态度"},
                    {"index": 6, "labelZh": "近期", "meaningZh": "即将发生的变化"},
                    {"index": 7, "labelZh": "自我", "meaningZh": "你在其中的角色与状态"},
                    {"index": 8, "labelZh": "环境", "meaningZh": "外部环境与他人影响"},
                    {"index": 9, "labelZh": "希望与恐惧", "meaningZh": "内心的期待与担忧"},
                    {"index": 10, "labelZh": "结果", "meaningZh": "综合后的可能结局"},
                ],
            },
            {
                "id": "relationship",
                "nameZh": "关系牌阵",
                "cardCount": 6,
                "complexity": "intermediate",
                "questionTypes": ["relationship", "love"],
                "positions": [
                    {"index": 1, "labelZh": "你", "meaningZh": "问事者在关系中的状态"},
                    {"index": 2, "labelZh": "对方", "meaningZh": "对方的状态与态度"},
                    {"index": 3, "labelZh": "关系现状", "meaningZh": "两人之间的互动模式"},
                    {"index": 4, "labelZh": "你的需求", "meaningZh": "你真正想要的是什么"},
                    {"index": 5, "labelZh": "对方需求", "meaningZh": "对方真正想要的是什么"},
                    {"index": 6, "labelZh": "走向", "meaningZh": "关系的可能发展"},
                ],
            },
            {
                "id": "two-choice",
                "nameZh": "二选一牌阵",
                "cardCount": 5,
                "complexity": "intermediate",
                "questionTypes": ["decision", "choice"],
                "positions": [
                    {"index": 1, "labelZh": "现状", "meaningZh": "你目前所处的局面"},
                    {"index": 2, "labelZh": "选项A", "meaningZh": "选择A的可能发展"},
                    {"index": 3, "labelZh": "选项B", "meaningZh": "选择B的可能发展"},
                    {"index": 4, "labelZh": "隐藏因素", "meaningZh": "尚未察觉的影响"},
                    {"index": 5, "labelZh": "建议", "meaningZh": "综合建议与倾向"},
                ],
            },
            {
                "id": "year-ahead",
                "nameZh": "年运牌阵",
                "cardCount": 12,
                "complexity": "advanced",
                "questionTypes": ["year", "forecast"],
                "positions": [
                    {"index": i, "labelZh": f"{i}月", "meaningZh": f"第{i}个月的主题与运势"}
                    for i in range(1, 13)
                ],
            },
        ]
    }


def write_rag_corpus(deck_name: str, cards: list[dict], out_name: str, source_note: str) -> dict:
    lines = [
        f"书名: {deck_name}",
        f"来源: {source_note}",
        f"整理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 50,
        "",
    ]
    for card in cards:
        lines.extend(
            [
                f"## {card['nameZh']} ({card['nameEn']})",
                f"牌ID: {card['id']}",
                "",
                "正位 (英文):",
                card.get("uprightEn", ""),
                "",
                "逆位 (英文):",
                card.get("reversedEn", ""),
                "",
                "正位 (中文):",
                card.get("uprightZh", ""),
                "",
                "逆位 (中文):",
                card.get("reversedZh", ""),
                "",
                "牌面描述:",
                card.get("descriptionEn", ""),
                "",
                "-" * 40,
                "",
            ]
        )
    path = OUT_DIR / out_name
    body = "\n".join(lines)
    path.write_text(body, encoding="utf-8")
    return {"file": out_name, "status": "ok", "chars": len(body)}


def download_rws_images(cards: list[dict]) -> dict:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    failed: list[str] = []
    for card in cards:
        card_id = card["id"]
        commons_file = card.get("commonsFile") or ""
        if not commons_file:
            failed.append(card_id)
            continue
        dest = IMAGE_DIR / f"{card_id}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            ok += 1
            continue
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{commons_file}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=120, allow_redirects=True)
            resp.raise_for_status()
            if "image" not in (resp.headers.get("Content-Type") or ""):
                failed.append(card_id)
                continue
            dest.write_bytes(resp.content)
            ok += 1
            print(f"  image ok: {card_id} <- {commons_file}")
            time.sleep(1.2)
        except Exception as exc:
            print(f"  image fail: {card_id} ({exc})")
            failed.append(card_id)
    return {"file": "rws images", "status": "ok" if ok else "partial", "ok": ok, "failed": failed}


def write_index(results: list[dict]) -> None:
    lines = [
        "塔罗占卜典籍 - 资料来源索引",
        "=" * 50,
        f"整理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"存放目录: {OUT_DIR}",
        "",
        "一、已生成本地文件",
        "",
    ]
    for item in results:
        line = f"- {item.get('file', '?')}: {item.get('status', 'unknown')}"
        if item.get("chars"):
            line += f" ({item['chars']} 字)"
        if item.get("ok"):
            line += f" (images ok={item['ok']})"
        if item.get("failed"):
            line += f" (failed={len(item['failed'])})"
        lines.append(line)
    lines.extend(
        [
            "",
            "二、来源说明",
            "",
            "- 韦特牌义: ekelen/tarot-api (MIT), 内容源自 A.E. Waite The Pictorial Key to the Tarot",
            "- 中文牌义: look-fate/tarot-lab (MIT)",
            "- 牌阵语义: 参考 TarotSchema/Tarotsmith (MIT + CC-BY 4.0, 使用时需署名)",
            "- sacred-texts.com / hermetic.com 抓取若被 403, 已改用上述开源数据生成 RAG 语料",
            "",
            "三、托特牌面版权",
            "",
            "- Thoth deck artwork (c) Ordo Templi Orientis; 本平台仅文字解读, 不复制牌面图像",
            "",
            "四、现代中文塔罗书",
            "",
            "- 《78度智慧》《其实你已经很塔罗》等现代出版物受版权保护, 请正版购买",
        ]
    )
    (OUT_DIR / "00_资料来源索引.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DECK_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    print("Fetching ekelen card_data.json ...")
    ekelen_raw = fetch_url(EKELEN_URL)
    ekelen = json.loads(ekelen_raw)
    print("Fetching tarot-lab cards.json ...")
    lab_raw = fetch_url(LAB_URL)
    lab_cards = json.loads(lab_raw)

    rws_cards = build_rws_cards(ekelen, lab_cards)
    marseille_cards = clone_deck(rws_cards, "marseille", "马赛塔罗")
    thoth_cards = clone_deck(rws_cards, "thoth", "托特塔罗")

    for deck, cards, label in [
        ("rws", rws_cards, "韦特塔罗"),
        ("marseille", marseille_cards, "马赛塔罗"),
        ("thoth", thoth_cards, "托特塔罗"),
    ]:
        path = DECK_DIR / f"deck_{deck}.json"
        payload = {"deck": deck, "nameZh": label, "cards": cards}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {path.name} ({len(cards)} cards)")
        results.append({"file": path.name, "status": "ok", "chars": len(cards)})

    spreads = build_spreads()
    spreads_path = DECK_DIR / "spreads.json"
    spreads_path.write_text(json.dumps(spreads, ensure_ascii=False, indent=2), encoding="utf-8")
    results.append({"file": spreads_path.name, "status": "ok"})

    results.append(
        write_rag_corpus(
            "韦特塔罗图钥 (Waite PKT 牌义汇编)",
            rws_cards,
            "韦特塔罗图钥-Waite-1911.txt",
            "ekelen/tarot-api MIT, 源自 The Pictorial Key to the Tarot (1911 public domain)",
        )
    )
    results.append(
        write_rag_corpus(
            "马赛塔罗牌义 (基线)",
            marseille_cards,
            "马赛塔罗-Papus-基线.txt",
            "基于韦特公版牌义基线; 完整 Papus 文本请见 sacred-texts.com/tarot/tob/",
        )
    )
    results.append(
        write_rag_corpus(
            "托特塔罗牌义 (基线)",
            thoth_cards,
            "托特之书牌义-Crowley-基线.txt",
            "文字基线; Crowley Book of Thoth 牌面图像受版权保护, 本平台不复制图像",
        )
    )

    print("Downloading RWS images (optional, skip with TAROT_SKIP_IMAGES=1) ...")
    import os

    if os.environ.get("TAROT_SKIP_IMAGES") == "1":
        results.append({"file": "rws images", "status": "skipped"})
    else:
        results.append(download_rws_images(rws_cards))

    write_index(results)
    print(f"\nDone. Output: {OUT_DIR} and {DECK_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
