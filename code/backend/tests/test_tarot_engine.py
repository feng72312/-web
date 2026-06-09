from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_tarot_decks_and_spreads():
    decks = client.get("/api/v1/tarot/decks")
    assert decks.status_code == 200
    body = decks.json()
    assert len(body["decks"]) == 3

    spreads = client.get("/api/v1/tarot/spreads")
    assert spreads.status_code == 200
    assert len(spreads.json()["spreads"]) >= 5


def test_tarot_draw_three_card():
    resp = client.post(
        "/api/v1/tarot/draw",
        json={
            "question": "这次换工作是否合适",
            "deck": "rws",
            "spread": "three-card",
            "allowReversed": True,
            "seed": 42,
        },
    )
    assert resp.status_code == 200
    reading = resp.json()["reading"]
    assert reading["spreadId"] == "three-card"
    assert len(reading["cards"]) == 3
    assert reading["cards"][0]["orientation"] in ("upright", "reversed")


def test_tarot_deck_cards():
    resp = client.get("/api/v1/tarot/deck/rws/cards")
    assert resp.status_code == 200
    cards = resp.json()["cards"]
    assert len(cards) == 78
    assert cards[0]["cardId"]
    assert cards[0]["nameZh"]


def test_tarot_reveal_is_repeatable():
    payload = {
        "question": "这次换工作是否合适",
        "deck": "rws",
        "spread": "three-card",
        "allowReversed": True,
        "sessionToken": "12345",
        "picks": [0, 7, 21],
    }
    first = client.post("/api/v1/tarot/reveal", json=payload)
    second = client.post("/api/v1/tarot/reveal", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["reading"]["cards"] == second.json()["reading"]["cards"]


@pytest.mark.parametrize(
    "picks",
    [
        [0, 0, 1],
        [0, 1],
        [0, 1, 99],
    ],
)
def test_tarot_reveal_rejects_invalid_picks(picks):
    resp = client.post(
        "/api/v1/tarot/reveal",
        json={
            "question": "今日运势",
            "deck": "rws",
            "spread": "three-card",
            "allowReversed": True,
            "sessionToken": "12345",
            "picks": picks,
        },
    )
    assert resp.status_code == 400


def test_tarot_build_manual_reading():
    resp = client.post(
        "/api/v1/tarot/build",
        json={
            "question": "今日运势",
            "deck": "rws",
            "spread": "three-card",
            "cards": [
                {"position": 1, "cardId": "major-01", "orientation": "upright"},
                {"position": 2, "cardId": "major-02", "orientation": "reversed"},
                {"position": 3, "cardId": "major-03", "orientation": "upright"},
            ],
        },
    )
    assert resp.status_code == 200
    cards = resp.json()["reading"]["cards"]
    assert cards[0]["nameZh"] == "魔术师"
    assert cards[1]["orientation"] == "reversed"
    assert cards[1]["meaningZh"]


@pytest.mark.parametrize(
    "cards",
    [
        [
            {"position": 1, "cardId": "major-01", "orientation": "upright"},
            {"position": 2, "cardId": "major-01", "orientation": "reversed"},
            {"position": 3, "cardId": "major-03", "orientation": "upright"},
        ],
        [
            {"position": 1, "cardId": "unknown", "orientation": "upright"},
            {"position": 2, "cardId": "major-02", "orientation": "reversed"},
            {"position": 3, "cardId": "major-03", "orientation": "upright"},
        ],
        [
            {"position": 1, "cardId": "major-01", "orientation": "upright"},
        ],
    ],
)
def test_tarot_build_rejects_invalid_cards(cards):
    resp = client.post(
        "/api/v1/tarot/build",
        json={
            "question": "今日运势",
            "deck": "rws",
            "spread": "three-card",
            "cards": cards,
        },
    )
    assert resp.status_code == 400


def test_tarot_suggest_spread():
    resp = client.post(
        "/api/v1/tarot/suggest-spread",
        json={"question": "我们还能复合吗"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["spreadId"] == "relationship"


def test_tarot_interpret_fallback():
    draw = client.post(
        "/api/v1/tarot/draw",
        json={
            "question": "今日运势",
            "deck": "thoth",
            "spread": "single",
            "allowReversed": True,
            "seed": 1,
        },
    )
    reading = draw.json()["reading"]
    resp = client.post(
        "/api/v1/tarot/interpret",
        json={"reading": reading, "style": "plain"},
    )
    assert resp.status_code == 200
    summary = resp.json()["interpretation"]["summary"]
    assert summary
