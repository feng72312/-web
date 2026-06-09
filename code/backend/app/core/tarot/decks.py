from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"

DECK_META = {
    "rws": {"nameZh": "韦特塔罗", "desc": "Rider-Waite-Smith, 现代塔罗主流体系"},
    "marseille": {"nameZh": "马赛塔罗", "desc": "Tarot de Marseille, 传统欧洲牌系"},
    "thoth": {"nameZh": "托特塔罗", "desc": "Crowley-Harris Thoth, 文字解读 (牌面无图像)"},
}


@lru_cache(maxsize=1)
def _load_all_decks() -> dict[str, dict[str, Any]]:
    decks: dict[str, dict[str, Any]] = {}
    for deck_id in DECK_META:
        path = DATA_DIR / f"deck_{deck_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"missing deck file: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        by_id = {card["id"]: card for card in payload.get("cards", [])}
        decks[deck_id] = {**payload, "byId": by_id}
    return decks


@lru_cache(maxsize=1)
def _load_spreads_raw() -> dict[str, Any]:
    path = DATA_DIR / "spreads.json"
    if not path.exists():
        raise FileNotFoundError(f"missing spreads file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_decks() -> list[dict[str, str]]:
    return [
        {"id": deck_id, "nameZh": meta["nameZh"], "desc": meta["desc"]}
        for deck_id, meta in DECK_META.items()
    ]


def list_deck_cards(deck_id: str) -> list[dict[str, Any]]:
    deck = get_deck(deck_id)
    cards: list[dict[str, Any]] = []
    for card in deck.get("cards", []):
        cards.append(
            {
                "cardId": card.get("id"),
                "nameZh": card.get("nameZh") or card.get("nameEn") or "",
                "nameEn": card.get("nameEn") or "",
                "image": card.get("image"),
                "keywordsZh": list(card.get("keywordsZh") or []),
            }
        )
    return cards


def get_deck(deck_id: str) -> dict[str, Any]:
    decks = _load_all_decks()
    if deck_id not in decks:
        raise ValueError(f"unknown deck: {deck_id}")
    return decks[deck_id]


def get_card(deck_id: str, card_id: str) -> dict[str, Any]:
    deck = get_deck(deck_id)
    card = deck["byId"].get(card_id)
    if card is None:
        raise ValueError(f"unknown card {card_id} in deck {deck_id}")
    return card


def list_spreads() -> list[dict[str, Any]]:
    payload = _load_spreads_raw()
    return payload.get("spreads", [])


def get_spread(spread_id: str) -> dict[str, Any]:
    for spread in list_spreads():
        if spread["id"] == spread_id:
            return spread
    raise ValueError(f"unknown spread: {spread_id}")
