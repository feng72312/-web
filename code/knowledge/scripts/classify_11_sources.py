"""Classify all files under 11紫微斗数 and emit ziwei_sources_manifest.json."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from decrypt_sources import run_decrypt
from source_manifest_ziwei import build_file_manifest, validate_manifest_files

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
SOURCE_11 = ROOT / "数据库" / "11紫微斗数"
MANIFEST_OUTPUT = KNOWLEDGE_DIR / "data" / "sources" / "ziwei_sources_manifest.json"
MIN_READABLE_CHARS = 32


def _probe_read_status(path: Path) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix == ".txt":
            text = path.read_text(encoding="utf-8", errors="replace")
            if len(text.strip()) < MIN_READABLE_CHARS:
                return "empty_or_unreadable"
            return "ok"
        if suffix in {".doc", ".docx"}:
            return "ok"
    except OSError:
        return "encrypted_or_unreadable"
    return "ok"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(SOURCE_11))
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--decrypt",
        action="store_true",
        help="run decrypt skill (file_decrypt.py) on source dir before scan",
    )
    args = parser.parse_args()
    source = Path(args.source)
    if not source.exists():
        print(f"source not found: {source}")
        return 1

    if args.decrypt and not args.validate_only:
        code = run_decrypt([source])
        if code != 0:
            print(f"[warn] decrypt exited with code {code}")

    if args.validate_only:
        if not MANIFEST_OUTPUT.is_file():
            print(f"manifest not found: {MANIFEST_OUTPUT}")
            return 1
        payload = json.loads(MANIFEST_OUTPUT.read_text(encoding="utf-8"))
        errors = validate_manifest_files(payload.get("files") or [], source)
        if errors:
            for err in errors:
                print(f"[error] {err}")
            return 2
        print("manifest validation ok")
        return 0

    normalized: list[dict] = []
    for rel_path in sorted(source.rglob("*")):
        path = rel_path
        if not path.is_file():
            continue
        if path.name.startswith("_") or path.name.startswith("~$"):
            continue
        if "_doc_backup" in path.parts:
            continue
        if path.suffix.lower() not in {".txt", ".doc", ".docx"}:
            continue
        rel_path = str(path.relative_to(source)).replace("\\", "/")
        row = build_file_manifest(rel_path)
        row["readStatus"] = _probe_read_status(path)
        normalized.append(row)

    by_authority: dict[str, int] = {}
    by_library: dict[str, int] = {}
    for row in normalized:
        at = str(row.get("authorityTier") or "?")
        lr = str(row.get("libraryRole") or "?")
        by_authority[at] = by_authority.get(at, 0) + 1
        by_library[lr] = by_library.get(lr, 0) + 1

    manifest_payload = {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "filesTotal": len(normalized),
        "byAuthorityTier": by_authority,
        "byLibraryRole": by_library,
        "files": normalized,
    }

    errors = validate_manifest_files(normalized, source)
    if errors:
        for err in errors:
            print(f"[warn] {err}")

    MANIFEST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUTPUT.write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest_payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
