from __future__ import annotations

import json
from pathlib import Path

from app.core.knowledge.keys import MONTH_LABEL_TO_ZHI, ZHI_TO_MONTH_LABEL
from app.core.knowledge.store import KnowledgeStore
from app.core.knowledge.service import KnowledgeService
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.rules import PaipanRules


def _chart(day_gan: str, month_zhi: str) -> dict:
    month_gan = "丙"
    return {
        "dayMaster": day_gan,
        "pillars": {
            "day": {"gan": day_gan, "zhi": "子", "ganzhi": f"{day_gan}子"},
            "month": {"gan": month_gan, "zhi": month_zhi, "ganzhi": f"{month_gan}{month_zhi}"},
            "year": {"gan": "庚", "zhi": "午", "ganzhi": "庚午"},
            "hour": {"gan": "丙", "zhi": "寅", "ganzhi": "丙寅"},
        },
        "sections": [],
    }


def test_keys_month_mapping() -> None:
    assert ZHI_TO_MONTH_LABEL["寅"] == "正月"
    assert MONTH_LABEL_TO_ZHI["正月"] == "寅"


def test_store_loads_graph(tmp_path: Path) -> None:
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    node = {
        "id": "tiaohou:甲:寅",
        "topic": "tiaohou",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "穷通宝鉴-明-余春台.txt",
        "lookupKey": {"dayGan": "甲", "monthZhi": "寅", "monthLabel": "正月"},
        "summary": "test summary",
        "claims": [
            {
                "classic": "穷通宝鉴",
                "edition": "余春台",
                "chapter": "test",
                "quote": "test quote",
                "conclusion": "test",
                "role": "primary",
                "aligns": None,
                "sourceFile": "穷通宝鉴-明-余春台.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
    }
    (graph_dir / "nodes.jsonl").write_text(json.dumps(node, ensure_ascii=False) + "\n", encoding="utf-8")
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")
    store = KnowledgeStore(tmp_path)
    store.load()
    assert store.enabled
    rows = store.lookup("tiaohou", {"dayGan": "甲", "monthZhi": "寅"})
    assert len(rows) == 1


def test_lookup_chart_finds_tiaohou(tmp_path: Path) -> None:
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    node = {
        "id": "tiaohou:甲:寅",
        "topic": "tiaohou",
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": "x.txt",
        "lookupKey": {"dayGan": "甲", "monthZhi": "寅", "monthLabel": "正月"},
        "summary": "初春尚有余寒, 得丙癸逢, 富贵双全",
        "claims": [
            {
                "classic": "穷通宝鉴",
                "edition": "",
                "chapter": "正月甲木",
                "quote": "quote",
                "conclusion": "c",
                "role": "primary",
                "aligns": None,
                "sourceFile": "x.txt",
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
    }
    (graph_dir / "nodes.jsonl").write_text(json.dumps(node, ensure_ascii=False) + "\n", encoding="utf-8")
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")
    service = KnowledgeService(KnowledgeStore(tmp_path))
    service.store.load()
    result = service.lookup_chart(_chart("甲", "寅"))
    assert result.hits
    assert result.hits[0].lookupKey["monthZhi"] == "寅"
    assert "shishen" in result.missingTopics


def test_safe_auto_answer_blocked_for_t3() -> None:
    from app.core.knowledge.tiers import allow_safe_auto_answer

    node = {
        "safeAutoAnswer": True,
        "sourceTier": "T3",
        "topic": "case",
        "agreementLevel": "single_source",
        "claims": [{"role": "primary"}],
        "domain": "bazi",
    }
    assert allow_safe_auto_answer(node) is False
