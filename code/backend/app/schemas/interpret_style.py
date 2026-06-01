from typing import Literal

from pydantic import field_validator

from app.core.agent.interpret_style import InterpretStyle, normalize_interpret_style

InterpretStyleField = Literal["professional", "plain"]


class InterpretStyleMixin:
    style: InterpretStyleField = "professional"

    @field_validator("style", mode="before")
    @classmethod
    def normalize_style(cls, value: object) -> InterpretStyle:
        if value is None:
            return "professional"
        return normalize_interpret_style(str(value))
