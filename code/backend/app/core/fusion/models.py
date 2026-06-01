from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

QuestionScope = Literal["life_outline", "event_detail", "mixed"]
PreferredChannel = Literal["agree", "bazi", "liuyao", "split"]


@dataclass
class ChannelVerdict:
    channel: str
    summary: str
    stance: str
    available: bool = True
    error: str = ""
    query: str = ""
    excerpts: list[dict[str, str]] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "summary": self.summary,
            "stance": self.stance,
            "available": self.available,
            "error": self.error,
            "query": self.query,
            "excerpts": self.excerpts,
            **self.extra,
        }


@dataclass
class FusionResult:
    question: str
    question_scope: QuestionScope
    agreed: bool
    preferred_channel: PreferredChannel
    bazi: ChannelVerdict
    liuyao: ChannelVerdict
    merged_summary: str
    weight_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "questionScope": self.question_scope,
            "agreed": self.agreed,
            "preferredChannel": self.preferred_channel,
            "weightNote": self.weight_note,
            "bazi": self.bazi.to_dict(),
            "liuyao": self.liuyao.to_dict(),
            "merged": {"summary": self.merged_summary},
        }
