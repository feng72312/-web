from __future__ import annotations

from app.core.agent.chat_scope import SCOPE_REFUSAL, is_chat_message_in_scope


def test_allows_fortune_telling_topics() -> None:
    allowed, refusal = is_chat_message_in_scope("帮我看看今年事业运势")
    assert allowed is True
    assert refusal is None


def test_allows_fuzzy_question() -> None:
    allowed, refusal = is_chat_message_in_scope("他还会回来吗")
    assert allowed is True
    assert refusal is None


def test_blocks_obvious_off_topic() -> None:
    allowed, refusal = is_chat_message_in_scope("用 python 写一个爬虫脚本")
    assert allowed is False
    assert refusal == SCOPE_REFUSAL


def test_blocks_empty_message() -> None:
    allowed, refusal = is_chat_message_in_scope(" ")
    assert allowed is False
    assert refusal
