import pytest

from app.core.ziwei.chart_enrich import compare_rule_change, enrich_palaces
from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules

pytest.importorskip("iztro_py")


def _sample_palaces() -> list[dict]:
    return [
        {
            "name": "命宫",
            "earthlyBranch": "子",
            "stemBranch": "甲子",
            "triadBranches": ["辰", "申"],
            "majorStars": [],
            "minorStars": [],
            "mutagenStars": [],
            "hasMalefic": False,
            "brightnessSummary": "",
        },
        {
            "name": "迁移",
            "earthlyBranch": "午",
            "stemBranch": "庚午",
            "triadBranches": ["寅", "戌"],
            "majorStars": [{"name": "紫微", "brightness": "庙"}],
            "minorStars": [],
            "mutagenStars": [],
            "hasMalefic": False,
            "brightnessSummary": "紫微庙",
        },
        {
            "name": "财帛",
            "earthlyBranch": "辰",
            "stemBranch": "戊辰",
            "triadBranches": ["子", "申"],
            "majorStars": [{"name": "天府", "brightness": "旺"}],
            "minorStars": [],
            "mutagenStars": [],
            "hasMalefic": True,
            "brightnessSummary": "天府旺",
        },
        {
            "name": "官禄",
            "earthlyBranch": "申",
            "stemBranch": "壬申",
            "triadBranches": ["子", "辰"],
            "majorStars": [{"name": "破军", "brightness": "陷"}],
            "minorStars": [],
            "mutagenStars": [{"name": "破军", "mutagen": "忌"}],
            "hasMalefic": True,
            "brightnessSummary": "破军陷",
        },
    ]


def test_empty_palace_borrows_opposite_major_stars() -> None:
    enriched = enrich_palaces(_sample_palaces())
    soul = enriched[0]
    assert soul["borrowedFromOpposite"] is True
    assert soul["borrowedMajorStars"] == ["紫微"]
    assert soul["palaceStrength"] == "borrowed"
    assert "borrowed_from_opposite" in soul["riskFlags"]


def test_triad_and_opposite_evidence_present() -> None:
    enriched = enrich_palaces(_sample_palaces())
    soul = enriched[0]
    assert soul["oppositeEvidence"]["name"] == "迁移"
    assert len(soul["triadEvidence"]) == 2
    assert {item["name"] for item in soul["triadEvidence"]} == {"财帛", "官禄"}


def test_palace_strength_and_risk_flags() -> None:
    enriched = enrich_palaces(_sample_palaces())
    wealth = next(item for item in enriched if item["name"] == "财帛")
    career = next(item for item in enriched if item["name"] == "官禄")
    assert wealth["palaceStrength"] == "strong"
    assert career["palaceStrength"] == "weak"
    assert "mutagen_ji" in career["riskFlags"]


def test_pro_chart_includes_enrichment_fields() -> None:
    engine = ZiweiEngine()
    result = engine.chart(
        ZiweiInput(
            calendar_type="solar",
            year=1990,
            month=5,
            day=15,
            hour=11,
            minute=30,
            gender=1,
            detail_level="pro",
            rules=ZiweiRules(),
        )
    )
    soul = result.chart["palaces"][0]
    assert "triadEvidence" in soul
    assert "oppositeEvidence" in soul
    assert "palaceStrength" in soul
    assert "riskFlags" in soul


def test_compare_rule_change_detects_mutagen_table_diff() -> None:
    engine = ZiweiEngine()
    base_input = ZiweiInput(
        calendar_type="solar",
        year=1990,
        month=5,
        day=15,
        hour=11,
        minute=30,
        gender=1,
        detail_level="pro",
        rules=ZiweiRules(mutagen_table="nan_pai"),
    )
    alt_input = ZiweiInput(
        calendar_type="solar",
        year=1990,
        month=5,
        day=15,
        hour=11,
        minute=30,
        gender=1,
        detail_level="pro",
        rules=ZiweiRules(mutagen_table="geng_beipai"),
    )
    before = engine.chart(base_input).chart
    after = engine.chart(alt_input).chart
    warnings = compare_rule_change(before, after)
    assert any("mutagenTable changed" in item for item in warnings)
    assert any("mutagen mapping changed" in item for item in warnings)


def test_rules_meta_present_on_chart() -> None:
    engine = ZiweiEngine()
    result = engine.chart(
        ZiweiInput(
            calendar_type="solar",
            year=1990,
            month=5,
            day=15,
            hour=11,
            minute=30,
            gender=1,
            detail_level="pro",
            rules=ZiweiRules(chart_school="feixing", mutagen_table="wu_pai"),
        )
    )
    rules_meta = result.chart["rulesMeta"]
    assert rules_meta["chartSchool"] == "feixing"
    assert rules_meta["mutagenTable"] == "wu_pai"
    assert "leapMonthRule" in rules_meta


def test_simple_chart_skips_enrichment_fields() -> None:
    engine = ZiweiEngine()
    result = engine.chart(
        ZiweiInput(
            calendar_type="solar",
            year=1990,
            month=5,
            day=15,
            hour=11,
            minute=30,
            gender=1,
            rules=ZiweiRules(),
        )
    )
    soul = result.chart["palaces"][0]
    assert "triadEvidence" not in soul
    assert "palaceStrength" not in soul


def test_borrowed_flag_only_when_opposite_has_major_stars() -> None:
    palaces = [
        {
            "name": "命宫",
            "earthlyBranch": "子",
            "triadBranches": ["辰", "申"],
            "majorStars": [],
            "minorStars": [],
            "mutagenStars": [],
            "hasMalefic": False,
        },
        {
            "name": "迁移",
            "earthlyBranch": "午",
            "triadBranches": ["寅", "戌"],
            "majorStars": [],
            "minorStars": [],
            "mutagenStars": [],
            "hasMalefic": False,
        },
    ]
    enriched = enrich_palaces(palaces)
    assert enriched[0]["borrowedFromOpposite"] is False
    assert enriched[0]["palaceStrength"] == "empty"
