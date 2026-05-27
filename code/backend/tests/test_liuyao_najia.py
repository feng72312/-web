from app.core.liuyao.engine import LiuyaoEngine
from app.core.liuyao.models import LiuyaoInput


def test_divine_coin_chart():
    engine = LiuyaoEngine()
    chart = engine.divine(
        LiuyaoInput(
            question="这次考试能过吗",
            method="coin",
            coin_lines=[7, 8, 9, 7, 6, 8],
            year=2026,
            month=5,
            day=27,
            hour=10,
        )
    ).to_dict()
    assert chart["benGua"]["name"]
    assert len(chart["lines"]) == 6
    assert chart["shiYing"]["shi"] in range(1, 7)
    assert chart["movingLines"] == [3, 5]
    assert chart["bianGua"] is not None


def test_najia_liuqin_present():
    engine = LiuyaoEngine()
    chart = engine.divine(
        LiuyaoInput(
            question="求财",
            method="coin",
            coin_lines=[7, 7, 7, 7, 7, 7],
        )
    ).to_dict()
    liuqin = {line["liuqin"] for line in chart["lines"]}
    assert "兄弟" in liuqin
