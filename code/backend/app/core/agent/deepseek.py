from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.agent.ai_text import sanitize_ai_text

logger = logging.getLogger(__name__)


class DeepSeekError(Exception):
    pass


class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com") -> None:
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _build_messages(
        self,
        system: str | None,
        history: list[dict[str, str]],
        user_message: str,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        for item in history:
            role = item.get("role", "")
            content = item.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})
        return messages

    async def chat_once(
        self,
        model: str,
        user_message: str,
        *,
        system: str | None = None,
        history: list[dict[str, str]] | None = None,
        temperature: float | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model,
            "messages": self._build_messages(system, history or [], user_message),
            "stream": False,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/v1/chat/completions",
                headers=self._headers(),
                json=payload,
            )
        if response.status_code >= 400:
            detail = response.text.strip() or f"HTTP {response.status_code}"
            raise DeepSeekError(detail)
        data = response.json()
        try:
            raw = str(data["choices"][0]["message"]["content"]).strip()
            return sanitize_ai_text(raw)
        except (KeyError, IndexError, TypeError) as err:
            raise DeepSeekError("invalid deepseek response") from err

    async def chat_stream(
        self,
        model: str,
        user_message: str,
        *,
        system: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncIterator[str]:
        payload = {
            "model": model,
            "messages": self._build_messages(system, history or [], user_message),
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/v1/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    detail = body.decode("utf-8", errors="replace").strip()
                    raise DeepSeekError(detail or f"HTTP {response.status_code}")
                async for line in response.aiter_lines():
                    chunk = self._parse_sse_line(line)
                    if chunk:
                        yield chunk

    def _parse_sse_line(self, line: str) -> str:
        trimmed = line.strip()
        if not trimmed or not trimmed.startswith("data:"):
            return ""
        data = trimmed[5:].strip()
        if data == "[DONE]":
            return ""
        try:
            payload: dict[str, Any] = json.loads(data)
        except json.JSONDecodeError:
            return ""
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""
        delta = choices[0].get("delta", {})
        if not isinstance(delta, dict):
            return ""
        content = delta.get("content")
        return content if isinstance(content, str) else ""


_client: DeepSeekClient | None = None


def init_deepseek_client(api_key: str, base_url: str = "https://api.deepseek.com") -> DeepSeekClient:
    global _client
    _client = DeepSeekClient(api_key=api_key, base_url=base_url)
    return _client


def get_deepseek_client() -> DeepSeekClient | None:
    return _client
