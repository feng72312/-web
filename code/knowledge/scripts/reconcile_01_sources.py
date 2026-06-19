"""Reconcile disk files, bazi_sources_manifest.json and index_report.json."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
DATA_DIR = ROOT / "数据库" / "01八字命理"
MANIFEST_PATH = KNOWLEDGE_DIR / "data" / "sources" / "bazi_sources_manifest.json"
INDEX_REPORT_PATH = ROOT / "code" / "rag" / "data" / "index_report.json"


def _disk_files() -> set[str]:
    names: set[str] = set()
    for path in DATA_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".doc", ".docx"}:
            names.add(str(path.relative_to(DATA_DIR)).replace("\\", "/"))
    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    if not MANIFEST_PATH.exists():
        print(f"missing manifest: {MANIFEST_PATH}")
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_files = {row["sourceFile"] for row in manifest.get("files", [])}
    disk = _disk_files()

    only_disk = sorted(disk - manifest_files)
    only_manifest = sorted(manifest_files - disk)

    index_info: dict = {}
    if INDEX_REPORT_PATH.exists():
        report = json.loads(INDEX_REPORT_PATH.read_text(encoding="utf-8"))
        for cat in report.get("categories", []):
            if cat.get("category") == "01八字命理":
                index_info = cat
                break

    tier_counter = Counter(row.get("authorityTier", "?") for row in manifest.get("files", []))
    role_counter = Counter(row.get("libraryRole", "?") for row in manifest.get("files", []))

    result = {
        "checkedAt": datetime.now().isoformat(timespec="seconds"),
        "diskFiles": len(disk),
        "manifestFiles": len(manifest_files),
        "indexFiles": index_info.get("files_total", 0),
        "indexChunks": index_info.get("chunks_total", 0),
        "onlyOnDisk": only_disk,
        "onlyInManifest": only_manifest,
        "byAuthorityTier": dict(tier_counter),
        "byLibraryRole": dict(role_counter),
        "aligned": not only_disk and not only_manifest and len(disk) == len(manifest_files),
    }

    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return 0 if result["aligned"] else 2


if __name__ == "__main__":
    sys.exit(main())
