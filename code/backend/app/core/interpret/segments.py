from __future__ import annotations

import re
from typing import Any

RULE_ID_TAG_RE = re.compile(r"\[ruleId:([^\]]+)\]")
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")


def _normalize_rule_ids(raw: str) -> list[str]:
    ids: list[str] = []
    for part in str(raw or "").replace("，", ",").split(","):
        rid = part.strip()
        if rid and rid not in ids:
            ids.append(rid)
    return ids


def _known_rule_id_set(judgement_report: dict[str, Any] | None, rule_id_refs: list[dict[str, str]]) -> set[str]:
    known: set[str] = set()
    for row in rule_id_refs or []:
        rid = str(row.get("ruleId") or "").strip()
        if rid:
            known.add(rid)
    report = judgement_report or {}
    for item in report.get("evidenceChain") or []:
        for rid in _normalize_rule_ids(str(item.get("ruleId") or "")):
            known.add(rid)
    for verdict in (report.get("arbitration") or {}).get("judgeOpinions") or []:
        for rid in verdict.get("ruleIds") or []:
            known.add(str(rid).strip())
    return {rid for rid in known if rid}


def _build_evidence_index(judgement_report: dict[str, Any] | None) -> dict[str, list[dict[str, str]]]:
    index: dict[str, list[dict[str, str]]] = {}
    for item in (judgement_report or {}).get("evidenceChain") or []:
        classic = str(item.get("primaryClassic") or "")
        conclusion = str(item.get("conclusion") or "")
        for rid in _normalize_rule_ids(str(item.get("ruleId") or "")):
            rows = index.setdefault(rid, [])
            rows.append(
                {
                    "ruleId": rid,
                    "classic": classic,
                    "conclusion": conclusion[:160],
                }
            )
    return index


def _strip_rule_id_tags(text: str) -> str:
    cleaned = RULE_ID_TAG_RE.sub("", text)
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def _split_paragraphs(text: str) -> list[str]:
    body = str(text or "").strip()
    if not body:
        return []
    parts = [part.strip() for part in PARAGRAPH_SPLIT_RE.split(body) if part.strip()]
    if len(parts) > 1:
        return parts
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if len(lines) <= 1:
        return [body]
    return lines


def _downgrade_confidence_band(band: str | None) -> str | None:
    if band == "strong":
        return "medium"
    if band == "medium":
        return "weak"
    return band


def build_interpret_segments(
    summary: str,
    judgement_report: dict[str, Any] | None,
    *,
    rule_id_refs: list[dict[str, str]] | None = None,
    confidence_band: str | None = None,
) -> dict[str, Any]:
    refs = list(rule_id_refs or [])
    known = _known_rule_id_set(judgement_report, refs)
    evidence_index = _build_evidence_index(judgement_report)
    ref_lookup = {str(row.get("ruleId") or "").strip(): row for row in refs if row.get("ruleId")}

    segments: list[dict[str, Any]] = []
    anchored = 0
    inference = 0

    for paragraph in _split_paragraphs(summary):
        tagged_ids: list[str] = []
        for match in RULE_ID_TAG_RE.finditer(paragraph):
            tagged_ids.extend(_normalize_rule_ids(match.group(1)))
        unique_ids: list[str] = []
        for rid in tagged_ids:
            if rid not in unique_ids:
                unique_ids.append(rid)

        rule_refs: list[dict[str, str]] = []
        evidence_refs: list[dict[str, str]] = []
        seen_evidence: set[str] = set()
        for rid in unique_ids:
            base = dict(ref_lookup.get(rid) or {"ruleId": rid})
            base["ruleId"] = rid
            base["verified"] = rid in known
            rule_refs.append(base)
            for ev in evidence_index.get(rid) or []:
                key = f"{ev.get('ruleId')}:{ev.get('conclusion')}"
                if key in seen_evidence:
                    continue
                seen_evidence.add(key)
                evidence_refs.append(ev)

        kind = "anchored" if rule_refs else "inference"
        if kind == "anchored":
            anchored += 1
        else:
            inference += 1

        segments.append(
            {
                "text": _strip_rule_id_tags(paragraph),
                "rawText": paragraph.strip(),
                "ruleIdRefs": rule_refs,
                "evidenceRefs": evidence_refs,
                "kind": kind,
            }
        )

    total = len(segments)
    anchored_ratio = (anchored / total) if total else 0.0
    adjusted_band = confidence_band
    confidence_note = ""
    if total and anchored_ratio < 0.5 and inference > 0:
        adjusted_band = _downgrade_confidence_band(confidence_band)
        confidence_note = "部分解读段落缺少规则锚点, 已标注为推断并下调置信度"

    return {
        "segments": segments,
        "stats": {
            "total": total,
            "anchored": anchored,
            "inference": inference,
            "anchoredRatio": round(anchored_ratio, 3),
        },
        "confidenceBand": adjusted_band,
        "confidenceNote": confidence_note,
    }
