"""Reorganize 数据库 into category folders and ingest pending texts."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from categories import CATEGORIES, SKIP_DUPLICATE_NAMES, legacy_target_folder

ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "数据库"
PENDING_DIR = ROOT / "未入库古籍" / "1"
ZIWEI_PENDING_DIR = ROOT / "未入库古籍" / "紫微斗数"
ZIWEI_CATEGORY = "11紫微斗数"
LEGACY_DIRS = [DB_DIR / "八字", DB_DIR / "梅花"]


def ensure_category_dirs() -> None:
    for folder, _ in CATEGORIES:
        (DB_DIR / folder).mkdir(parents=True, exist_ok=True)


def unique_target(folder: Path, filename: str) -> Path:
    target = folder / filename
    if not target.exists():
        return target
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    for i in range(2, 100):
        candidate = folder / f"{stem}__dup{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"cannot allocate unique name for {filename}")


def move_file(src: Path, dest: Path, log: list[dict]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    log.append({"action": "move", "from": str(src), "to": str(dest)})


def import_pending(log: list[dict]) -> int:
    if not PENDING_DIR.exists():
        return 0
    count = 0
    for folder_name, _ in CATEGORIES:
        src_dir = PENDING_DIR / folder_name
        if not src_dir.is_dir():
            continue
        dest_dir = DB_DIR / folder_name
        for src in sorted(src_dir.glob("*")):
            if not src.is_file():
                continue
            if src.suffix.lower() not in {".txt", ".doc", ".docx"}:
                continue
            if src.name in SKIP_DUPLICATE_NAMES:
                log.append({"action": "skip_duplicate", "file": src.name})
                continue
            dest = unique_target(dest_dir, src.name)
            move_file(src, dest, log)
            count += 1
    return count


def import_ziwei_pending(log: list[dict]) -> int:
    if not ZIWEI_PENDING_DIR.exists():
        return 0
    dest_dir = DB_DIR / ZIWEI_CATEGORY
    count = 0
    for src in sorted(ZIWEI_PENDING_DIR.glob("*")):
        if not src.is_file():
            continue
        if src.suffix.lower() not in {".txt", ".doc", ".docx"}:
            continue
        if src.name in SKIP_DUPLICATE_NAMES:
            log.append({"action": "skip_duplicate", "file": src.name})
            continue
        dest = unique_target(dest_dir, src.name)
        move_file(src, dest, log)
        count += 1
    return count


def migrate_legacy(log: list[dict]) -> int:
    count = 0
    for legacy_root in LEGACY_DIRS:
        if not legacy_root.exists():
            continue
        for src in sorted(legacy_root.rglob("*")):
            if not src.is_file():
                continue
            if src.suffix.lower() not in {".txt", ".doc", ".docx"}:
                continue
            folder_name = legacy_target_folder(src)
            dest_dir = DB_DIR / folder_name
            dest = unique_target(dest_dir, src.name)
            move_file(src, dest, log)
            count += 1
    return count


def cleanup_empty_dirs() -> None:
    for legacy_root in LEGACY_DIRS:
        if not legacy_root.exists():
            continue
        for path in sorted(legacy_root.rglob("*"), reverse=True):
            if path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
        try:
            legacy_root.rmdir()
        except OSError:
            pass
    if PENDING_DIR.exists():
        for path in sorted(PENDING_DIR.rglob("*"), reverse=True):
            if path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
    if ZIWEI_PENDING_DIR.exists():
        for path in sorted(ZIWEI_PENDING_DIR.rglob("*"), reverse=True):
            if path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
        try:
            ZIWEI_PENDING_DIR.rmdir()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate library files to category folders")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("dry-run not implemented; use without flag to migrate")
        return 1

    ensure_category_dirs()
    log: list[dict] = []
    pending_n = import_pending(log)
    ziwei_n = import_ziwei_pending(log)
    legacy_n = migrate_legacy(log)
    cleanup_empty_dirs()

    report = {
        "migrated_at": datetime.now().isoformat(timespec="seconds"),
        "pending_imported": pending_n,
        "ziwei_imported": ziwei_n,
        "legacy_migrated": legacy_n,
        "entries": log,
    }
    out = Path(__file__).resolve().parent / "data" / "migrate_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {"pending_imported": pending_n, "ziwei_imported": ziwei_n, "legacy_migrated": legacy_n},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
