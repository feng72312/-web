from app.core.ziwei.judgement.mutagen_judge import MutagenJudge


def test_mutagen_judge_outputs_directional_events() -> None:
    chart = {
        "palaces": [
            {
                "name": "夫妻",
                "mutagenStars": [],
                "flyingMutagens": {
                    "outbound": [
                        {
                            "mutagen": "忌",
                            "star": "太阴",
                            "targetPalace": "命宫",
                            "targetBranch": "子",
                        }
                    ],
                    "inbound": [],
                },
            },
            {
                "name": "命宫",
                "mutagenStars": [],
                "flyingMutagens": {
                    "outbound": [],
                    "inbound": [
                        {
                            "mutagen": "忌",
                            "star": "太阴",
                            "sourcePalace": "夫妻",
                            "sourceStem": "甲",
                            "sourceBranch": "午",
                        }
                    ],
                },
            },
        ]
    }
    verdict = MutagenJudge().judge(chart)
    events = verdict.flags.get("events") or []
    assert events
    assert any(
        item.get("fromPalace") == "夫妻"
        and item.get("toPalace") == "命宫"
        and item.get("mutagenType") == "忌"
        for item in events
    )
    assert "夫妻" in verdict.summary and "命宫" in verdict.summary
