from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.utils.zhuge_engine import compute_qian_number, divine_three_chars, reduce_stroke, stroke_count
from app.main import app

client = TestClient(app)


def test_reduce_stroke_rules() -> None:
    assert reduce_stroke(12) == 2
    assert reduce_stroke(10) == 0
    assert reduce_stroke(7) == 7


def test_compute_qian_number_example() -> None:
    qian_no, steps = compute_qian_number(7, 9, 2)
    assert qian_no == 24
    assert any("24" in step for step in steps)


def test_divine_with_explicit_strokes() -> None:
    result = divine_three_chars("\u4f51\u54b1\u7edf", strokes=[7, 9, 12])
    assert result["qianNo"] == 24
    assert len(result["chars"]) == 3


def test_zhuge_divine_endpoint() -> None:
    response = client.post(
        "/api/v1/utils/zhuge/divine",
        json={"chars": "\u4f51\u54b1\u7edf", "strokes": [7, 9, 12]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["qianNo"] == 24


def test_stroke_count_without_zhuge_table_uses_naming_fallback(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.core.utils.zhuge_engine._load_strokes",
        lambda: {},
    )
    assert stroke_count("\u4e00") == 8


def test_zhuge_qian_384_present() -> None:
    from app.core.utils.zhuge_engine import _load_qian

    qian = _load_qian()
    assert qian.get("231", "").startswith("目下意难舒")
    assert "孔颜" in qian.get("384", "")
    assert len(qian) >= 384


def test_jiemeng_search_endpoint() -> None:
    response = client.post(
        "/api/v1/utils/jiemeng/search",
        json={"dream": "\u5929\u95e8\u5f00"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["matches"]
    assert "天门" in data["matches"][0]["text"]
