from __future__ import annotations

from pathlib import Path


def utils_data_dir() -> Path:
    """Runtime JSON for zhuge/jiemeng/naming utils.

    Prefer bundled files under app/data (Docker image). Fall back to backend/data
    for local development when app/data is not populated.
    """
    app_root = Path(__file__).resolve().parents[2]
    bundled = app_root / "data"
    if bundled.is_dir() and any(bundled.glob("*.json")):
        return bundled
    legacy = app_root.parent / "data"
    if legacy.is_dir():
        return legacy
    return bundled
