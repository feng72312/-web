from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatModel:
    id: str
    label: str
    tag: str
    provider: str


CHAT_MODELS: tuple[ChatModel, ...] = (
    ChatModel("composer-2.5", "Composer 2.5", "Fast", "cursor"),
    ChatModel("deepseek-chat", "DeepSeek Chat", "Chat", "deepseek"),
    ChatModel("deepseek-reasoner", "DeepSeek Reasoner", "Reasoner", "deepseek"),
    ChatModel("deepseek-v4-flash", "DeepSeek V4 Flash", "Flash", "deepseek"),
    ChatModel("deepseek-v4-pro", "DeepSeek V4 Pro", "Pro", "deepseek"),
)


def model_by_id(model_id: str) -> ChatModel | None:
    normalized = model_id.strip().lower()
    for item in CHAT_MODELS:
        if item.id == normalized:
            return item
    return None


def list_models(*, cursor_enabled: bool, deepseek_enabled: bool) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in CHAT_MODELS:
        if item.provider == "cursor" and not cursor_enabled:
            continue
        if item.provider == "deepseek" and not deepseek_enabled:
            continue
        rows.append(
            {
                "id": item.id,
                "label": item.label,
                "tag": item.tag,
                "provider": item.provider,
            }
        )
    return rows


def default_model(*, cursor_enabled: bool, deepseek_enabled: bool) -> str:
    if deepseek_enabled:
        return "deepseek-chat"
    if cursor_enabled:
        return "composer-2.5"
    return "deepseek-chat"
