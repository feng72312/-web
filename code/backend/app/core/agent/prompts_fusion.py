from __future__ import annotations

from app.core.agent.interpret_style import InterpretStyle
from app.core.agent.prompts import build_interpret_prompt
from app.core.agent.prompts_liuyao import build_liuyao_interpret_prompt
from typing import Any

STANCE_SUFFIX = (
    "\n\n文末必须单独一行, 格式严格为: 倾向:吉 或 倾向:凶 或 倾向:平 或 倾向:未定"
)


def build_bazi_channel_prompt(
    chart: dict[str, Any],
    question: str,
    *,
    compressed=None,
    rag_excerpts: list[dict[str, str]] | None = None,
    style: InterpretStyle = "professional",
) -> str:
    base = build_interpret_prompt(
        chart,
        compressed=compressed,
        rag_excerpts=rag_excerpts,
        style=style,
    )
    return (
        f"{base}\n\n"
        f"用户问事: {question}\n"
        f"请从八字命局、大运流年角度回答, 控制在 350 字以内."
        f"{STANCE_SUFFIX}"
    )


def build_liuyao_channel_prompt(
    chart: dict[str, Any],
    yong_shen: dict[str, Any],
    excerpts: list[dict[str, str]],
    question: str,
    *,
    style: InterpretStyle = "professional",
) -> str:
    base = build_liuyao_interpret_prompt(chart, yong_shen, excerpts, style=style)
    return (
        f"{base}\n\n"
        f"问事重点: {question}\n"
        f"请就此事占断, 控制在 350 字以内."
        f"{STANCE_SUFFIX}"
    )


def parse_stance(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("倾向:"):
            value = line.split(":", 1)[-1].strip()
            if value in ("吉", "凶", "平", "未定"):
                return value
    return "未定"
