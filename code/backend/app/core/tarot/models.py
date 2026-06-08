from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

CardOrientation = Literal["upright", "reversed"]
DeckId = Literal["rws", "marseille", "thoth"]


@dataclass
class TarotInput:
    question: str
    deck: str
    spread: str
    allow_reversed: bool = True
    seed: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "deck": self.deck,
            "spread": self.spread,
            "allowReversed": self.allow_reversed,
            "seed": self.seed,
        }


@dataclass
class DrawnCard:
    position: int
    position_label: str
    position_meaning: str
    card_id: str
    name_zh: str
    name_en: str
    orientation: CardOrientation
    meaning_zh: str
    meaning_en: str
    keywords: list[str]
    image: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": self.position,
            "positionLabel": self.position_label,
            "positionMeaning": self.position_meaning,
            "cardId": self.card_id,
            "nameZh": self.name_zh,
            "nameEn": self.name_en,
            "orientation": self.orientation,
            "meaningZh": self.meaning_zh,
            "meaningEn": self.meaning_en,
            "keywords": self.keywords,
            "image": self.image,
        }


@dataclass
class TarotReading:
    input: TarotInput
    deck: str
    deck_name: str
    spread_id: str
    spread_name: str
    cards: list[DrawnCard]
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": self.input.to_dict(),
            "deck": self.deck,
            "deckName": self.deck_name,
            "spreadId": self.spread_id,
            "spreadName": self.spread_name,
            "cards": [card.to_dict() for card in self.cards],
            "meta": self.meta,
        }
