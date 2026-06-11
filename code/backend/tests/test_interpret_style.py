from app.core.agent.interpret_style import normalize_interpret_style, style_mode_block
from app.core.agent.prompts_liuren import build_liuren_interpret_prompt
from app.core.agent.prompts_liuyao import build_liuyao_interpret_prompt
from app.core.agent.prompts_qimen import build_qimen_interpret_prompt
from app.schemas.interpret_style import InterpretStyleMixin
from pydantic import BaseModel


class SampleRequest(BaseModel, InterpretStyleMixin):
    pass


def test_normalize_interpret_style() -> None:
    assert normalize_interpret_style("plain") == "plain"
    assert normalize_interpret_style("professional") == "professional"
    assert normalize_interpret_style(None) == "professional"


def test_style_mixin_defaults() -> None:
    req = SampleRequest()
    assert req.style == "professional"


def test_liuyao_prompt_includes_plain_mode() -> None:
    chart = {
        "benGua": {"name": "乾为天"},
        "bianGua": None,
        "movingLines": [],
        "lines": [],
        "input": {"question": "测试"},
        "monthJian": "子",
        "dayChen": "午",
    }
    yong_shen = {"yongShen": "妻财", "position": 3, "reason": "test"}
    pro = build_liuyao_interpret_prompt(chart, yong_shen, [], style="professional")
    plain = build_liuyao_interpret_prompt(chart, yong_shen, [], style="plain")
    assert "专业解读" in pro
    assert "AI深度解读" in plain
    assert "### 总断" in style_mode_block("plain")
    assert style_mode_block("plain") in plain


def test_qimen_prompt_builds_with_four_pillars() -> None:
    chart = {
        "input": {"question": "测试", "category": "shizhan", "direction": ""},
        "ju": {"juName": "阳遁三局", "jieqi": "立夏"},
        "zhiFuZhiShi": {"zhiFuStar": "天辅", "zhiFuGong": "巽"},
        "palaces": [],
        "fourPillars": {"year": "乙巳", "month": "辛巳", "day": "甲子", "hour": "己巳"},
        "trueSolarTime": "2025-05-29 10:30",
    }
    plain = build_qimen_interpret_prompt(chart, [], [], style="plain")
    assert "乙巳" in plain
    assert style_mode_block("plain") in plain


def test_liuren_prompt_builds_with_four_pillars() -> None:
    chart = {
        "input": {"question": "测试"},
        "liuren": {"fourPillars": {"day": "甲子"}, "shenSha": {"guiRen": "丑"}},
        "siKe": {},
    }
    plain = build_liuren_interpret_prompt(chart, [], [], style="plain")
    assert "甲子" in plain
    assert style_mode_block("plain") in plain
