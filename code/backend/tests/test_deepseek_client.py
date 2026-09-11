from __future__ import annotations

from app.core.agent.deepseek import DeepSeekClient


def test_deepseek_base_url_strips_environment_whitespace() -> None:
    client = DeepSeekClient(" test-key\r\n", " https://api.deepseek.com/\r\n")

    assert client._api_key == "test-key"
    assert client._base_url == "https://api.deepseek.com"
