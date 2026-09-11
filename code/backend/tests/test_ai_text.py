from app.core.agent.ai_text import sanitize_ai_text, strip_agent_protocol


def test_strips_ai_generated_footer():
    raw = (
        "### 总断\n\n"
        "近期事业有起色.\n\n"
        "以上推算由AI生成，仅供娱乐参考。"
    )
    cleaned = sanitize_ai_text(raw)
    assert "仅供娱乐" not in cleaned
    assert "以上推算" not in cleaned
    assert "近期事业有起色" in cleaned


def test_strips_deepseek_footer():
    raw = (
        "### 签解\n\n"
        "**签文原文**\n"
        "> 事未宽，心不安\n\n"
        "---\n"
        "以上内容由DeepSeek生成，仅供娱乐参考。玄学虽有趣，生活更值得用心经营。"
    )
    cleaned = sanitize_ai_text(raw)
    assert "DeepSeek" not in cleaned
    assert "---" not in cleaned
    assert "签解" in cleaned
    assert "事未宽" in cleaned


def test_strips_dual_mode_tags_and_lookup_preamble() -> None:
    raw = (
        "[MODE: RESEARCH]\n\n"
        "你问的是「我是谁」，且要求结合上文命盘资料。"
        "我先在人物包与相关资料里查找老子的命盘/身份信息。\n"
        "[MODE: RESEARCH]\n\n"
        "我是李耳，字聃，世称老子。\n\n"
        "周朝守藏室之史——管的是典籍，不是兵马。"
    )
    cleaned = sanitize_ai_text(raw)
    assert "[MODE:" not in cleaned
    assert cleaned.startswith("我是李耳")
    assert "查找老子" not in cleaned
    assert strip_agent_protocol(raw).startswith("我是李耳")


def test_strips_single_newline_lookup_then_body() -> None:
    raw = (
        "[MODE: RESEARCH]\n\n"
        "你问「我是谁」，且要求结合上文命盘资料；"
        "我先在会话与工作区里查找是否已有你的命盘信息。\n"
        "你问「我是谁」——好问题。世人常把名字当答案。"
    )
    cleaned = sanitize_ai_text(raw)
    assert "[MODE:" not in cleaned
    assert cleaned.startswith("你问「我是谁」——好问题")
    assert "查找是否已有" not in cleaned


def test_keeps_research_word_in_body() -> None:
    raw = "我信的是道。后世研究《道德经》者众，我只写了五千言。"
    cleaned = sanitize_ai_text(raw)
    assert "研究" in cleaned
    assert cleaned == raw
