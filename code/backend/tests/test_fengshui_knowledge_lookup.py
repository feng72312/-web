from __future__ import annotations

from app.core.knowledge.service import KnowledgeService
from app.core.knowledge.store import KnowledgeStore
from pathlib import Path


def test_lookup_fengshui_bazhai_chart():
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "knowledge" / "data"
    store = KnowledgeStore(data_dir)
    store.load()
    svc = KnowledgeService(store)
    chart = {
        "input": {
            "method": "bazhai",
            "scene": "residence",
            "sittingMountain": "zi",
            "birthYear": 1985,
            "gender": 1,
        },
        "mingGua": {"number": 6, "name": "乾", "groupLabel": "西四命"},
        "zhaiGua": {"number": 1, "name": "坎", "groupLabel": "东四宅", "label": "坐子向午"},
        "directions": [
            {"label": "生气", "auspicious": True},
            {"label": "延年", "auspicious": True},
        ],
    }
    result = svc.lookup_fengshui_chart(chart)
    assert result.hits
    topics = {hit.topic for hit in result.hits}
    assert "shan" in topics or "scene" in topics


def test_lookup_fengshui_xuankong_chart():
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "knowledge" / "data"
    store = KnowledgeStore(data_dir)
    store.load()
    svc = KnowledgeService(store)
    chart = {
        "input": {"method": "xuankong", "buildYear": 2020, "sittingMountain": "hai"},
        "xuankong": {
            "period": {"number": 8, "label": "8运"},
            "combinedPan": [{"yunStar": 8, "shanStar": 6, "xiangStar": 4, "palace": "中"}],
        },
    }
    result = svc.lookup_fengshui_chart(chart)
    assert any(hit.topic == "period" for hit in result.hits)
