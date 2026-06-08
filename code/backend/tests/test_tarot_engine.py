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
