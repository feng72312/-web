from __future__ import annotations

from pathlib import Path

from app.core.quota.persistence import ensure_persist_marker, inspect_sqlite_path


def test_inspect_local_sqlite_not_persistent(tmp_path: Path) -> None:
    db_path = tmp_path / "quota.db"
    db_path.write_bytes(b"sqlite")
    info = inspect_sqlite_path(db_path)
    assert info["fileExists"] is True
    assert info["likelyPersistent"] is False


def test_ensure_persist_marker_creates_file(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "quota.db"
    ensure_persist_marker(db_path)
    marker = tmp_path / "data" / ".bazi_persist_marker"
    assert marker.is_file()
    assert marker.read_text(encoding="utf-8").startswith("bazi-persist-")
