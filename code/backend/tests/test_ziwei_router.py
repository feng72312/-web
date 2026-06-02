from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ziwei_rules_endpoint() -> None:
    r = client.get("/api/v1/ziwei/rules")
    assert r.status_code == 200
    data = r.json()
    assert data["defaults"]["leapMonthRule"] == "next_month"


def test_ziwei_chart_endpoint() -> None:
    try:
        import iztro_py  # noqa: F401
    except ImportError:
        return
    r = client.post(
        "/api/v1/ziwei/chart",
        json={
            "calendarType": "solar",
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 11,
            "minute": 30,
            "gender": 1,
        },
    )
    assert r.status_code == 200
    chart = r.json()["chart"]
    assert len(chart["palaces"]) == 12
