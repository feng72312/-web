from __future__ import annotations

from typing import Annotated, Any

from pydantic import BeforeValidator


def _coerce_rag_excerpt_item(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        msg = "excerpt item must be a dict"
        raise TypeError(msg)
    result: dict[str, str] = {}
    for key, raw in value.items():
        if raw is None:
            continue
        result[str(key)] = raw if isinstance(raw, str) else str(raw)
    return result


def _coerce_rag_excerpt_list(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        msg = "excerpts must be a list"
        raise TypeError(msg)
    return [_coerce_rag_excerpt_item(item) for item in value]


def _coerce_optional_rag_excerpt_list(value: Any) -> list[dict[str, str]] | None:
    if value is None:
        return None
    return _coerce_rag_excerpt_list(value)


RagExcerptDict = Annotated[dict[str, str], BeforeValidator(_coerce_rag_excerpt_item)]
RagExcerptList = Annotated[list[dict[str, str]], BeforeValidator(_coerce_rag_excerpt_list)]
OptionalRagExcerptList = Annotated[
    list[dict[str, str]] | None,
    BeforeValidator(_coerce_optional_rag_excerpt_list),
]
