"""Infer target year from free-text questions without benchmark dataset imports."""

from __future__ import annotations

import re

YEAR_RE = re.compile(r"(20\d{2})")


def infer_target_year(question: str) -> int | None:
    matches = [int(m.group(1)) for m in YEAR_RE.finditer(question or "")]
    if not matches:
        return None
    return matches[-1]
