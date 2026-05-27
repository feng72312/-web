from app.core.liuyao.yong_shen_service import YongShenService, fallback_yong_shen


def test_fallback_exam_uses_parents():
    chart = {
        "lines": [
            {"position": 1, "liuqin": "子孙", "stem": "甲", "branch": "子"},
            {"position": 2, "liuqin": "妻财", "stem": "乙", "branch": "丑"},
            {"position": 3, "liuqin": "父母", "stem": "丙", "branch": "寅"},
            {"position": 4, "liuqin": "官鬼", "stem": "丁", "branch": "卯"},
            {"position": 5, "liuqin": "兄弟", "stem": "戊", "branch": "辰"},
            {"position": 6, "liuqin": "父母", "stem": "己", "branch": "巳"},
        ],
        "shiYing": {"shi": 5, "ying": 2},
    }
    result = fallback_yong_shen(chart, "这次考试能过吗")
    assert result.yong_shen == "父母"
    assert result.position == 3
    assert result.source == "fallback"


def test_manual_override():
    service = YongShenService()
    chart = {
        "lines": [
            {"position": i, "liuqin": name, "stem": "甲", "branch": "子"}
            for i, name in enumerate(
                ["子孙", "妻财", "兄弟", "官鬼", "父母", "兄弟"],
                start=1,
            )
        ],
        "shiYing": {"shi": 1, "ying": 4},
    }
    result = service.apply_override(chart, "官鬼")
    assert result.yong_shen == "官鬼"
    assert result.position == 4
    assert result.source == "manual"
