from app.core.agent.ai_text import sanitize_ai_text


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
