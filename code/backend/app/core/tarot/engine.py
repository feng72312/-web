from __future__ import annotations

import random
import re
import secrets
from typing import Any

from app.core.tarot.decks import get_card, get_deck, get_spread
from app.core.tarot.models import DrawnCard, TarotInput, TarotReading


class TarotEngine:
    def draw(self, inp: TarotInput) -> TarotReading:
        deck = get_deck(inp.deck)
        spread = get_spread(inp.spread)
        positions = spread.get("positions") or []
        count = int(spread.get("cardCount") or len(positions))
        if len(positions) != count:
            raise ValueError(f"spread {inp.spread} position count mismatch")
        if count > len(deck.get("cards", [])):
            raise ValueError("spread requires more cards than deck has")

        rng: random.Random | secrets.SystemRandom
        if inp.seed is not None:
            rng = random.Random(inp.seed)
        else:
            rng = secrets.SystemRandom()

        pool = list(deck.get("cards", []))
        rng.shuffle(pool)
        picked = pool[:count]

        drawn: list[DrawnCard] = []
        for index, (pos, card_raw) in enumerate(zip(positions, picked), start=1):
            reversed_flag = inp.allow_reversed and rng.random() < 0.5
            orientation = "reversed" if reversed_flag else "upright"
            if reversed_flag:
                meaning_zh = card_raw.get("reversedZh") or card_raw.get("reversedEn") or ""
                meaning_en = card_raw.get("reversedEn") or ""
            else:
                meaning_zh = card_raw.get("uprightZh") or card_raw.get("uprightEn") or ""
                meaning_en = card_raw.get("uprightEn") or ""
            if meaning_zh and not re.search(r"[\u4e00-\u9fff]", meaning_zh):
                meaning_zh = meaning_en
            drawn.append(
                DrawnCard(
                    position=int(pos.get("index") or index),
                    position_label=str(pos.get("labelZh") or f"位置{index}"),
                    position_meaning=str(pos.get("meaningZh") or ""),
                    card_id=str(card_raw["id"]),
                    name_zh=str(card_raw.get("nameZh") or card_raw.get("nameEn") or ""),
                    name_en=str(card_raw.get("nameEn") or ""),
                    orientation=orientation,
                    meaning_zh=meaning_zh,
                    meaning_en=meaning_en,
                    keywords=list(card_raw.get("keywordsZh") or []),
                    image=card_raw.get("image"),
                )
            )

        return TarotReading(
            input=inp,
            deck=inp.deck,
            deck_name=str(deck.get("nameZh") or inp.deck),
            spread_id=inp.spread,
            spread_name=str(spread.get("nameZh") or inp.spread),
            cards=drawn,
            meta={
                "cardCount": count,
                "drawNote": f"{deck.get('nameZh', inp.deck)} / {spread.get('nameZh', inp.spread)}",
            },
        )

    def reading_dict(self, inp: TarotInput) -> dict[str, Any]:
        return self.draw(inp).to_dict()
