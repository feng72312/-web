from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.interpret_style import InterpretStyleMixin


class TarotDrawRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    deck: Literal["rws", "marseille", "thoth"]
    spread: str = Field(min_length=1, max_length=40)
    allowReversed: bool = True
    seed: int | None = None

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()


class TarotSuggestSpreadRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()


class TarotShuffleRequest(BaseModel):
    deck: Literal["rws", "marseille", "thoth"]
    allowReversed: bool = True


class TarotShuffleResponse(BaseModel):
    sessionToken: str
    deckSize: int


class TarotRevealRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    deck: Literal["rws", "marseille", "thoth"]
    spread: str = Field(min_length=1, max_length=40)
    allowReversed: bool = True
    sessionToken: str = Field(min_length=1, max_length=40)
    picks: list[int]

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()


class TarotManualCard(BaseModel):
    position: int
    cardId: str = Field(min_length=1, max_length=40)
    orientation: Literal["upright", "reversed"]


class TarotBuildRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)
    deck: Literal["rws", "marseille", "thoth"]
    spread: str = Field(min_length=1, max_length=40)
    cards: list[TarotManualCard]

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()


class TarotRagSearchRequest(BaseModel):
    reading: dict[str, Any]
    question: str | None = None


class TarotInterpretRequest(BaseModel, InterpretStyleMixin):
    reading: dict[str, Any]
    question: str | None = None
    excerpts: list[dict[str, str]] | None = None
    model: str | None = None


class TarotChatInitRequest(BaseModel):
    reading: dict[str, Any]
    excerpts: list[dict[str, str]] | None = None


class TarotDrawResponse(BaseModel):
    reading: dict[str, Any]


class TarotSuggestSpreadResponse(BaseModel):
    spreadId: str
    reason: str


class TarotRagSearchResponse(BaseModel):
    query: str
    excerpts: list[dict[str, str]]


class TarotInterpretResponse(BaseModel):
    reading: dict[str, Any]
    interpretation: dict[str, Any]


class TarotDecksResponse(BaseModel):
    decks: list[dict[str, str]]


class TarotSpreadsResponse(BaseModel):
    spreads: list[dict[str, Any]]


class TarotDeckCardsResponse(BaseModel):
    cards: list[dict[str, Any]]
