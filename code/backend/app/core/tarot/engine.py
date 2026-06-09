from __future__ import annotations

import random
import re
import secrets
from typing import Any

from app.core.tarot.decks import get_card, get_deck, get_spread
from app.core.tarot.models import DrawnCard, TarotInput, TarotReading


class TarotEngine:
    def _spread_positions(self, spread_id: str) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
        spread = get_spread(spread_id)
        positions = spread.get("positions") or []
        count = int(spread.get("cardCount") or len(positions))
        if len(positions) != count:
            raise ValueError(f"spread {spread_id} position count mismatch")
        return spread, positions, count

    def _make_drawn_card(
        self,
        pos: dict[str, Any],
        card_raw: dict[str, Any],
        orientation: str,
        index: int,
    ) -> DrawnCard:
        if orientation not in ("upright", "reversed"):
            raise ValueError(f"invalid orientation: {orientation}")

        if orientation == "reversed":
            meaning_zh = card_raw.get("reversedZh") or card_raw.get("reversedEn") or ""
            meaning_en = card_raw.get("reversedEn") or ""
        else:
            meaning_zh = card_raw.get("uprightZh") or card_raw.get("uprightEn") or ""
            meaning_en = card_raw.get("uprightEn") or ""
        if meaning_zh and not re.search(r"[\u4e00-\u9fff]", meaning_zh):
            meaning_zh = meaning_en

        return DrawnCard(
            position=int(pos.get("index") or index),
            position_label=str(pos.get("labelZh") or f"位置{index}"),
            position_meaning=str(pos.get("meaningZh") or ""),
            card_id=str(card_raw["id"]),
            name_zh=str(card_raw.get("nameZh") or card_raw.get("nameEn") or ""),
            name_en=str(card_raw.get("nameEn") or ""),
            orientation=orientation,  # type: ignore[arg-type]
            meaning_zh=meaning_zh,
            meaning_en=meaning_en,
            keywords=list(card_raw.get("keywordsZh") or []),
            image=card_raw.get("image"),
        )

    def draw(self, inp: TarotInput) -> TarotReading:
        deck = get_deck(inp.deck)
        spread, positions, count = self._spread_positions(inp.spread)
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
            drawn.append(self._make_drawn_card(pos, card_raw, orientation, index))

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

    def shuffle(self, deck_id: str) -> tuple[str, int]:
        deck = get_deck(deck_id)
        seed = str(secrets.randbits(64))
        return seed, len(deck.get("cards", []))

    def reveal(
        self,
        question: str,
        deck_id: str,
        spread_id: str,
        allow_reversed: bool,
        seed: str,
        picks: list[int],
    ) -> TarotReading:
        deck = get_deck(deck_id)
        spread, positions, count = self._spread_positions(spread_id)
        pool = list(deck.get("cards", []))
        if count > len(pool):
            raise ValueError("spread requires more cards than deck has")
        if len(picks) != count:
            raise ValueError(f"expected {count} picks")
        if len(set(picks)) != len(picks):
            raise ValueError("picks must be unique")
        if any(pick < 0 or pick >= len(pool) for pick in picks):
            raise ValueError("pick index out of range")

        try:
            seed_int = int(seed)
        except ValueError as err:
            raise ValueError("invalid session token") from err

        rng = random.Random(seed_int)
        rng.shuffle(pool)
        orientations = [
            "reversed" if allow_reversed and rng.random() < 0.5 else "upright"
            for _ in pool
        ]
        drawn = [
            self._make_drawn_card(positions[index], pool[pick], orientations[pick], index + 1)
            for index, pick in enumerate(picks)
        ]
        return TarotReading(
            input=TarotInput(
                question=question,
                deck=deck_id,
                spread=spread_id,
                allow_reversed=allow_reversed,
                seed=seed_int,
            ),
            deck=deck_id,
            deck_name=str(deck.get("nameZh") or deck_id),
            spread_id=spread_id,
            spread_name=str(spread.get("nameZh") or spread_id),
            cards=drawn,
            meta={
                "cardCount": count,
                "drawNote": f"{deck.get('nameZh', deck_id)} / {spread.get('nameZh', spread_id)}",
                "drawMode": "pick",
            },
        )

    def build(
        self,
        question: str,
        deck_id: str,
        spread_id: str,
        manual: list[dict[str, Any]],
    ) -> TarotReading:
        deck = get_deck(deck_id)
        spread, positions, count = self._spread_positions(spread_id)
        if len(manual) != count:
            raise ValueError(f"expected {count} cards")

        ordered = sorted(manual, key=lambda item: int(item.get("position", 0)))
        expected_positions = [int(pos.get("index") or index) for index, pos in enumerate(positions, start=1)]
        actual_positions = [int(item.get("position", 0)) for item in ordered]
        if actual_positions != expected_positions:
            raise ValueError("manual positions do not match spread")

        card_ids = [str(item.get("cardId") or "") for item in ordered]
        if len(set(card_ids)) != len(card_ids):
            raise ValueError("cards must be unique")

        drawn: list[DrawnCard] = []
        for index, (pos, item) in enumerate(zip(positions, ordered), start=1):
            card_raw = get_card(deck_id, str(item.get("cardId") or ""))
            orientation = str(item.get("orientation") or "upright")
            drawn.append(self._make_drawn_card(pos, card_raw, orientation, index))

        return TarotReading(
            input=TarotInput(
                question=question,
                deck=deck_id,
                spread=spread_id,
                allow_reversed=True,
            ),
            deck=deck_id,
            deck_name=str(deck.get("nameZh") or deck_id),
            spread_id=spread_id,
            spread_name=str(spread.get("nameZh") or spread_id),
            cards=drawn,
            meta={
                "cardCount": count,
                "drawNote": f"{deck.get('nameZh', deck_id)} / {spread.get('nameZh', spread_id)}",
                "drawMode": "manual",
            },
        )
