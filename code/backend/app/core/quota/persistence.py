from __future__ import annotations

import os
import time
from pathlib import Path

MARKER_NAME = ".bazi_persist_marker"


def cos_mount_detected() -> bool:
    """Return True when /mnt is backed by COS/FUSE (not container ephemeral overlay)."""
    try:
        mounts = Path("/proc/mounts").read_text(encoding="utf-8")
    except OSError:
        return False
    for line in mounts.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        mount_point = parts[1]
        if mount_point != "/mnt" and not mount_point.startswith("/mnt/"):
            continue
        fs_type = parts[2] if len(parts) > 2 else ""
        source = parts[0]
        if "fuse" in fs_type.lower() or "cos" in source.lower():
            return True
    return False


def inspect_sqlite_path(db_path: Path) -> dict[str, object]:
    """Return diagnostics for a SQLite file used by quota or stats."""
    path = db_path.expanduser()
    parent = path.parent
    parent_exists = parent.exists()
    file_exists = path.is_file()
    file_size = path.stat().st_size if file_exists else 0
    file_mtime = path.stat().st_mtime if file_exists else None

    marker_path = parent / MARKER_NAME
    marker_exists = marker_path.is_file()
    marker_value = ""
    if marker_exists:
        try:
            marker_value = marker_path.read_text(encoding="utf-8").strip()
        except OSError:
            marker_value = ""

    on_cos_mount = str(path).replace("\\", "/").startswith("/mnt/")
    mount_root = Path("/mnt")
    mount_root_exists = mount_root.is_dir()
    mount_writable = os.access(mount_root, os.W_OK) if mount_root_exists else False
    cos_mounted = cos_mount_detected()

    likely_persistent = on_cos_mount and cos_mounted and file_exists

    return {
        "dbPath": str(path),
        "parentExists": parent_exists,
        "fileExists": file_exists,
        "fileSizeBytes": int(file_size),
        "fileModifiedAt": float(file_mtime) if file_mtime is not None else None,
        "onCosMountPath": on_cos_mount,
        "cosMountDetected": cos_mounted,
        "mountRootExists": mount_root_exists,
        "mountRootWritable": mount_writable,
        "markerExists": marker_exists,
        "markerValue": marker_value,
        "likelyPersistent": likely_persistent,
    }


def ensure_persist_marker(db_path: Path) -> None:
    """Write a marker beside the SQLite file so redeploy can be verified."""
    parent = db_path.expanduser().parent
    parent.mkdir(parents=True, exist_ok=True)
    marker_path = parent / MARKER_NAME
    if marker_path.is_file():
        return
    payload = f"bazi-persist-{int(time.time())}"
    marker_path.write_text(payload, encoding="utf-8")
