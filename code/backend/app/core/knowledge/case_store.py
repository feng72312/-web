from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.knowledge.case_match import (
    case_has_readable_body,
    is_applicable_case,
    readable_verdict_excerpt,
    score_case_match,
)

logger = logging.getLogger(__name__)


class CaseExperienceStore:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._cases: list[dict] = []
        self._enabled = False
        self._load_error: str | None = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def load_error(self) -> str | None:
        return self._load_error

    def load(self) -> None:
        case_path = self._data_dir / "cases" / "cases.jsonl"
        if not case_path.exists():
            self._enabled = False
            self._load_error = f"cases not found: {case_path}"
            logger.warning("case store disabled: %s", self._load_error)
            return
        rows: list[dict] = []
        for line in case_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        self._cases = rows
        self._enabled = True
        self._load_error = None
        applicable = sum(1 for row in rows if is_applicable_case(row))
        logger.info("case store loaded cases=%s applicable=%s", len(rows), applicable)

    def match_chart(self, chart: dict, *, limit: int = 3) -> list[dict]:
        if not self._enabled:
            return []
        scored: list[tuple[int, dict]] = []
        for row in self._cases:
            score = score_case_match(row, chart)
            if score > 0:
                scored.append((score, row))
        scored.sort(
            key=lambda item: (
                item[0],
                1 if case_has_readable_body(item[1]) else 0,
                len(str(item[1].get("verdict") or "")),
            ),
            reverse=True,
        )
        hits = [row for _, row in scored[:limit]]
        if hits:
            return hits
        fallback_scored: list[tuple[int, dict]] = []
        for row in self._cases:
            if not is_applicable_case(row):
                continue
            readability = 2 if case_has_readable_body(row) else 0
            fallback_scored.append((readability, row))
        fallback_scored.sort(key=lambda item: item[0], reverse=True)
        return [row for _, row in fallback_scored[:limit]]

    def to_case_reference(self, row: dict) -> dict:
        excerpt = readable_verdict_excerpt(str(row.get("verdict") or ""))
        if not excerpt:
            excerpt = str(row.get("verdict", ""))[:300]
        return {
            "source": row.get("sourceFile", ""),
            "classic": row.get("classic", ""),
            "authorityTier": row.get("authorityTier", "C"),
            "evidenceRole": "case_reference",
            "evidenceBucket": "caseReference",
            "libraryRole": row.get("libraryRole", "experience_library"),
            "canJudge": False,
            "forbiddenApply": row.get("forbiddenApply", True),
            "structureTags": row.get("structureTags", []),
            "eventTags": row.get("eventTags", []),
            "eventYear": row.get("eventYear", []),
            "observedEvent": row.get("observedEvent", ""),
            "chartPattern": row.get("chartPattern", ""),
            "luckTrigger": row.get("luckTrigger", []),
            "doNotApplyReason": row.get("doNotApplyReason", ""),
            "excerpt": excerpt,
            "confidence": row.get("confidence", "low"),
        }

    def stats(self) -> dict:
        applicable = sum(1 for row in self._cases if is_applicable_case(row))
        return {
            "enabled": self._enabled,
            "caseCount": len(self._cases),
            "applicableCount": applicable,
            "loadError": self._load_error,
        }
