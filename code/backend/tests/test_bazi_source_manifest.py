from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "code" / "knowledge" / "data" / "sources" / "bazi_sources_manifest.json"


def test_bazi_manifest_exists() -> None:
    assert MANIFEST.is_file(), f"missing manifest: {MANIFEST}"


def test_manifest_has_three_library_roles() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    roles = set((payload.get("byLibraryRole") or {}).keys())
    assert "judge_library" in roles
    assert "experience_library" in roles


def test_qiongtong_is_primary_judge() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = payload.get("files") or []
    qiongtong = next(
        (
            r
            for r in rows
            if str(r.get("sourceFile", "")).endswith("穷通宝鉴-明-余春台.txt")
        ),
        None,
    )
    assert qiongtong is not None
    assert qiongtong.get("authorityTier") == "S"
    assert qiongtong.get("canJudge") is True
    assert qiongtong.get("evidenceRole") == "tiaohou_judge"


def test_case_file_with_classic_name_stays_experience_library() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = payload.get("files") or []
    case_row = next(
        (r for r in rows if "全部命例" in str(r.get("sourceFile", ""))),
        None,
    )
    assert case_row is not None
    assert case_row.get("legacyTier") == "T3"
    assert case_row.get("authorityTier") == "C"
    assert case_row.get("libraryRole") == "experience_library"
    assert case_row.get("canJudge") is False
    assert case_row.get("evidenceRole") == "case_reference"
