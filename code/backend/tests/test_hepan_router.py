from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PERSON_A = {
    "name": "\u7532",
    "calendarType": "solar",
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 10,
    "minute": 0,
    "gender": 1,
}

PERSON_B = {
    "name": "\u4e59",
    "calendarType": "solar",
    "year": 1992,
    "month": 8,
    "day": 20,
    "hour": 14,
    "minute": 0,
    "gender": 0,
}


def test_hepan_scenes_endpoint() -> None:
    r = client.get("/api/v1/hepan/scenes")
    assert r.status_code == 200
    data = r.json()
    assert len(data["scenes"]) == 3
    assert data["scenes"][0]["id"] == "romance"


def test_hepan_chart_bazi() -> None:
    r = client.post(
        "/api/v1/hepan/chart",
        json={
            "personA": PERSON_A,
            "personB": PERSON_B,
            "scene": "partnership",
            "discipline": "bazi",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["discipline"] == "bazi"
    assert data["crossNotes"]
    assert data["personA"]["baziChart"]
    assert data["personB"]["baziChart"]


def test_hepan_chart_same_person_rejected() -> None:
    r = client.post(
        "/api/v1/hepan/chart",
        json={
            "personA": PERSON_A,
            "personB": PERSON_A,
            "scene": "marriage",
            "discipline": "bazi",
        },
    )
    assert r.status_code == 400


def test_hepan_chart_ziwei() -> None:
    try:
        import iztro_py  # noqa: F401
    except ImportError:
        return
    r = client.post(
        "/api/v1/hepan/chart",
        json={
            "personA": PERSON_A,
            "personB": PERSON_B,
            "scene": "marriage",
            "discipline": "ziwei",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["discipline"] == "ziwei"
    assert data["personA"]["ziweiChart"]
    assert data["crossNotes"]
