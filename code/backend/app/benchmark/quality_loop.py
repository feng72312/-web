from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.benchmark.contest8_eval import run_eval


@dataclass
class QualitySnapshot:
    timestamp: str
    contest8_accuracy: float | None = None
    contest8_total: int = 0
    online_feedback_positive: int = 0
    online_feedback_negative: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "contest8Accuracy": self.contest8_accuracy,
            "contest8Total": self.contest8_total,
            "onlineFeedbackPositive": self.online_feedback_positive,
            "onlineFeedbackNegative": self.online_feedback_negative,
            "notes": self.notes,
        }


class QualityLoop:
    """Contest8 offline eval + online feedback aggregation."""

    def __init__(self, store_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[2] / "data"
        self._store_path = store_path or (root / "quality_snapshots.jsonl")

    async def run_contest8_snapshot(self, *, limit: int | None = None) -> QualitySnapshot:
        ts = datetime.now(timezone.utc).isoformat()
        try:
            result = await run_eval(split="dev", limit=limit or 20)
            acc = float(result.accuracy)
            total = int(result.total)
            return QualitySnapshot(
                timestamp=ts,
                contest8_accuracy=acc,
                contest8_total=total,
                notes=[f"contest8 run limit={limit}"],
            )
        except Exception as err:
            return QualitySnapshot(
                timestamp=ts,
                notes=[f"contest8 skipped: {err}"],
            )

    def record_feedback(self, *, positive: bool, module: str, note: str = "") -> None:
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "type": "feedback",
            "positive": positive,
            "module": module,
            "note": note,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._store_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def append_snapshot(self, snapshot: QualitySnapshot) -> None:
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        with self._store_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(snapshot.to_dict(), ensure_ascii=False) + "\n")
