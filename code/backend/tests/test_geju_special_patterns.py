from __future__ import annotations

from app.core.knowledge.geju_special import detect_geju_special_patterns


WEAK_WEALTH_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 1, "火": 1, "土": 1, "金": 4, "水": 1},
    "pillars": {
        "year": {"gan": "庚", "zhi": "申", "shishenGan": "七杀", "shishenZhi": ["七杀", "偏财"]},
        "month": {"gan": "辛", "zhi": "酉", "shishenGan": "正官", "shishenZhi": ["正官"]},
        "day": {"gan": "甲", "zhi": "子", "shishenGan": "", "shishenZhi": ["正印"]},
        "hour": {"gan": "庚", "zhi": "午", "shishenGan": "七杀", "shishenZhi": ["伤官", "正财"]},
    },
}

GAN_HE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 2, "火": 1, "土": 2, "金": 1, "水": 2},
    "pillars": {
        "year": {"gan": "甲", "zhi": "子", "shishenGan": "比肩"},
        "month": {"gan": "己", "zhi": "丑", "shishenGan": "正财"},
        "day": {"gan": "甲", "zhi": "午", "shishenGan": ""},
        "hour": {"gan": "乙", "zhi": "亥", "shishenGan": "劫财"},
    },
}

CHONG_CHART = {
    "dayMaster": "壬",
    "dayMasterWuxing": "水",
    "wuxingCount": {"木": 1, "火": 1, "土": 1, "金": 1, "水": 2},
    "pillars": {
        "year": {"gan": "丙", "zhi": "子", "shishenGan": "偏财"},
        "month": {"gan": "庚", "zhi": "午", "shishenGan": "偏印"},
        "day": {"gan": "壬", "zhi": "寅", "shishenGan": ""},
        "hour": {"gan": "甲", "zhi": "午", "shishenGan": "食神"},
    },
}


def test_detect_boundary_patterns_always_present() -> None:
    patterns = detect_geju_special_patterns(GAN_HE_CHART)
    for key in ("zagai", "waige", "jishen_po", "xionshen_cheng"):
        assert key in patterns


def test_detect_huaji_from_gan_he() -> None:
    patterns = detect_geju_special_patterns(GAN_HE_CHART)
    assert "huaji" in patterns


def test_detect_congcai_when_weak_and_wealthy_without_root() -> None:
    patterns = detect_geju_special_patterns(WEAK_WEALTH_CHART)
    assert "congcai" in patterns
    assert "congsha" in patterns


def test_detect_congcai_suppressed_when_branch_has_root() -> None:
    has_root_chart = {
        **WEAK_WEALTH_CHART,
        "pillars": {
            **WEAK_WEALTH_CHART["pillars"],
            "month": {
                "gan": "甲",
                "zhi": "酉",
                "shishenGan": "比肩",
                "shishenZhi": ["正官"],
            },
        },
    }
    patterns = detect_geju_special_patterns(has_root_chart)
    assert "congcai" not in patterns


def test_detect_congcai_when_weak_without_root() -> None:
    no_root_chart = {
        "dayMaster": "甲",
        "dayMasterWuxing": "木",
        "wuxingCount": {"木": 1, "火": 1, "土": 1, "金": 4, "水": 1},
        "pillars": {
            "year": {"gan": "庚", "zhi": "申", "shishenGan": "七杀", "shishenZhi": ["七杀", "偏财"]},
            "month": {"gan": "辛", "zhi": "酉", "shishenGan": "正官", "shishenZhi": ["正官"]},
            "day": {"gan": "甲", "zhi": "申", "shishenGan": "", "shishenZhi": ["七杀", "偏财"]},
            "hour": {"gan": "庚", "zhi": "午", "shishenGan": "七杀", "shishenZhi": ["伤官", "正财"]},
        },
    }
    patterns = detect_geju_special_patterns(no_root_chart)
    assert "congcai" in patterns
    assert "congsha" in patterns


def test_detect_daochong_from_zhi_clash() -> None:
    patterns = detect_geju_special_patterns(CHONG_CHART)
    assert "daochong" in patterns


def test_geju_judge_uses_conditional_special_patterns() -> None:
    from app.core.judgement.judges import GejuJudge
    from app.core.knowledge.factory import get_knowledge_service

    service = get_knowledge_service()
    verdict = GejuJudge().judge(GAN_HE_CHART)
    assert verdict.role == "geju"
    if service.enabled:
        assert any(rule_id.startswith("geju:special:huaji") for rule_id in verdict.ruleIds)
