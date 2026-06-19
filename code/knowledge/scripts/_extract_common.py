"""Shared helpers for classic rule extraction scripts."""

from __future__ import annotations

import re
from pathlib import Path


def read_source_text(path: Path) -> str:
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def trim_summary(text: str, limit: int = 120) -> str:
    cleaned = re.sub(r"\s+", "", text)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "..."


def make_node(
    *,
    node_id: str,
    topic: str,
    source_file: str,
    lookup_key: dict[str, str],
    summary: str,
    quote: str,
    classic: str,
    chapter: str,
    edition: str = "",
    rule_type: str = "",
    evidence_role: str = "",
    authority_tier: str = "S",
) -> dict:
    node: dict = {
        "id": node_id,
        "topic": topic,
        "sourceTier": "T1",
        "sourceCategory": "01八字命理",
        "sourceFile": source_file,
        "lookupKey": lookup_key,
        "summary": trim_summary(summary),
        "claims": [
            {
                "classic": classic,
                "edition": edition,
                "chapter": chapter,
                "quote": quote[:500],
                "conclusion": trim_summary(summary, 80),
                "role": "primary",
                "aligns": None,
                "sourceFile": source_file,
                "sourceCategory": "01八字命理",
            }
        ],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "bazi",
        "reviewedAt": None,
    }
    if rule_type:
        node["ruleType"] = rule_type
    if evidence_role:
        node["evidenceRole"] = evidence_role
        node["authorityTier"] = authority_tier
    return node
