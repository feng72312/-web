"""Load bazi / liuyao / ziwei source manifests for RAG chunk metadata."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BAZI_MANIFEST_PATH = ROOT / "code" / "knowledge" / "data" / "sources" / "bazi_sources_manifest.json"
LIUYAO_MANIFEST_PATH = ROOT / "code" / "knowledge" / "data" / "sources" / "liuyao_sources_manifest.json"
ZIWEI_MANIFEST_PATH = ROOT / "code" / "knowledge" / "data" / "sources" / "ziwei_sources_manifest.json"
FALLBACK_INDEX = ROOT / "code" / "knowledge" / "data" / "sources" / "01_index.json"

_bazi_cache: dict[str, dict] | None = None
_liuyao_cache: dict[str, dict] | None = None
_ziwei_cache: dict[str, dict] | None = None


def _default_from_tier(source_file: str, tier: str) -> dict:
    authority = {"T1": "S", "T2": "A", "T3": "C", "T4": "D"}.get(tier, "D")
    library_role = "judge_library" if authority in ("S", "A", "B") else (
        "experience_library" if authority == "C" else "supplement_library"
    )
    evidence_role = {
        "S": "primary_judge",
        "A": "secondary_support",
        "B": "modern_explanation",
        "C": "case_reference",
        "D": "low_trust",
    }.get(authority, "low_trust")
    return {
        "sourceFile": source_file,
        "authorityTier": authority,
        "evidenceRole": evidence_role,
        "sourceType": "classic" if authority in ("S", "A") else "misc",
        "libraryRole": library_role,
        "canJudge": authority in ("S", "A"),
        "canOverride": authority == "S",
        "canEnterProductionRag": library_role != "supplement_library",
        "judgmentPolicy": "can_primary_judge" if authority in ("S", "A") else (
            "case_only_no_judge" if authority == "C" else "exclude_or_low_trust"
        ),
        "domains": ["general"],
        "topicScope": ["general"],
    }


def _load_manifest_rows(path: Path) -> dict[str, dict]:
    index: dict[str, dict] = {}
    if not path.is_file():
        return index
    payload = json.loads(path.read_text(encoding="utf-8"))
    for row in payload.get("files") or []:
        key = str(row.get("sourceFile") or "").replace("\\", "/")
        if key:
            index[key] = row
    return index


def load_bazi_manifest_index() -> dict[str, dict]:
    global _bazi_cache
    if _bazi_cache is not None:
        return _bazi_cache

    index = _load_manifest_rows(BAZI_MANIFEST_PATH)
    if not index and FALLBACK_INDEX.is_file():
        payload = json.loads(FALLBACK_INDEX.read_text(encoding="utf-8"))
        for row in payload.get("files") or []:
            key = str(row.get("sourceFile") or "")
            if key:
                index[key] = _default_from_tier(key, str(row.get("tier") or "T4"))

    _bazi_cache = index
    return index


def load_liuyao_manifest_index() -> dict[str, dict]:
    global _liuyao_cache
    if _liuyao_cache is not None:
        return _liuyao_cache

    _liuyao_cache = _load_manifest_rows(LIUYAO_MANIFEST_PATH)
    return _liuyao_cache


def load_ziwei_manifest_index() -> dict[str, dict]:
    global _ziwei_cache
    if _ziwei_cache is not None:
        return _ziwei_cache

    _ziwei_cache = _load_manifest_rows(ZIWEI_MANIFEST_PATH)
    return _ziwei_cache


def load_manifest_index() -> dict[str, dict]:
    merged = dict(load_bazi_manifest_index())
    merged.update(load_liuyao_manifest_index())
    merged.update(load_ziwei_manifest_index())
    return merged


def _category_from_rel(rel_path: str) -> str:
    normalized = rel_path.replace("\\", "/")
    if normalized.startswith("02六爻卜筮/"):
        return "02六爻卜筮"
    if normalized.startswith("01八字命理/"):
        return "01八字命理"
    if normalized.startswith("11紫微斗数/"):
        return "11紫微斗数"
    return ""


def _lookup_in_index(index: dict[str, dict], file_name: str, rel_path: str) -> dict | None:
    if file_name in index:
        return dict(index[file_name])

    normalized = rel_path.replace("\\", "/") if rel_path else ""
    if normalized:
        if normalized in index:
            return dict(index[normalized])
        if "/" in normalized:
            tail = normalized.split("/", 1)[1]
            if tail in index:
                return dict(index[tail])
        alt_doc = normalized.replace(".txt", ".doc")
        alt_txt = normalized.replace(".doc", ".txt")
        for candidate in (alt_doc, alt_txt):
            if candidate in index:
                return dict(index[candidate])
            if "/" in candidate:
                tail = candidate.split("/", 1)[1]
                if tail in index:
                    return dict(index[tail])

    for key, row in index.items():
        if key.endswith(file_name) or file_name.endswith(key):
            return dict(row)

    if normalized:
        suffix = normalized.split("/")[-1]
        if suffix in index:
            return dict(index[suffix])

    return None


def lookup_file_meta(file_name: str, rel_path: str = "") -> dict:
    category = _category_from_rel(rel_path)
    if category == "02六爻卜筮":
        hit = _lookup_in_index(load_liuyao_manifest_index(), file_name, rel_path)
        if hit:
            return hit
        return _default_from_tier(file_name, "T4")
    if category == "11紫微斗数":
        hit = _lookup_in_index(load_ziwei_manifest_index(), file_name, rel_path)
        if hit:
            return hit
        return _default_from_tier(file_name, "T4")

    hit = _lookup_in_index(load_bazi_manifest_index(), file_name, rel_path)
    if hit:
        return hit

    hit = _lookup_in_index(load_liuyao_manifest_index(), file_name, rel_path)
    if hit:
        return hit

    hit = _lookup_in_index(load_ziwei_manifest_index(), file_name, rel_path)
    if hit:
        return hit

    return _default_from_tier(file_name, "T4")


def clear_manifest_cache() -> None:
    global _bazi_cache, _liuyao_cache, _ziwei_cache
    _bazi_cache = None
    _liuyao_cache = None
    _ziwei_cache = None
