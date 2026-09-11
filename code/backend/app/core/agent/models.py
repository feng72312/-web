from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatModel:
    id: str
    label: str
    tag: str
    provider: str
    tier: str
    tier_rank: int


CHAT_MODELS: tuple[ChatModel, ...] = (
    ChatModel("composer-2.5", "Composer 2.5", "Agent", "cursor", "大师B", 2),
    ChatModel("deepseek-chat", "DeepSeek Chat", "Chat", "deepseek", "小师傅", 1),
    ChatModel("deepseek-reasoner", "DeepSeek Reasoner", "Reasoner", "deepseek", "大师", 2),
    ChatModel("deepseek-v4-pro", "DeepSeek V4 Pro", "Pro", "deepseek", "资深道长", 3),
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
                "label": item.tier,
                "tag": item.tag,
                "provider": item.provider,
                "tier": item.tier,
                "tierRank": item.tier_rank,
            }
        )
    return rows


def default_model(*, cursor_enabled: bool, deepseek_enabled: bool) -> str:
    if cursor_enabled:
        return "composer-2.5"
    return "deepseek-chat"


def tier_for_model(model_id: str | None) -> str:
    if not model_id:
        return "小师傅"
    item = model_by_id(model_id)
    return item.tier if item else "小师傅"
