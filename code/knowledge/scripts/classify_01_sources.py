"""Classify all files under 01八字命理 by source tier and three-library manifest."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from source_manifest import build_file_manifest, classify_legacy_tier

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
SOURCE_01 = ROOT / "数据库" / "01八字命理"
OUTPUT = KNOWLEDGE_DIR / "data" / "sources" / "01_index.json"
MANIFEST_OUTPUT = KNOWLEDGE_DIR / "data" / "sources" / "bazi_sources_manifest.json"


def classify_file(name: str) -> str:
    return classify_legacy_tier(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(SOURCE_01))
    args = parser.parse_args()
    source = Path(args.source)
    if not source.exists():
        print(f"source not found: {source}")
        return 1

    files: list[dict] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".txt", ".doc", ".docx"}:
            continue
        rel = str(path.relative_to(ROOT / "数据库"))
        tier = classify_file(path.name)
        files.append(
            {
                "sourceCategory": "01八字命理",
                "sourceFile": rel.replace("\\", "/").split("/", 1)[1]
                if rel.startswith("01")
                else path.name,
                "relativePath": str(path.relative_to(ROOT / "数据库")).replace("\\", "/"),
                "tier": tier,
                "topicsAttempted": [],
            }
        )

    # normalize sourceFile to be relative to category folder
    normalized: list[dict] = []
    for item in files:
        rel_path = item["relativePath"]
        if rel_path.startswith("01八字命理/"):
            source_file = rel_path[len("01八字命理/") :]
        else:
            source_file = rel_path
        normalized.append(
            {
                "sourceCategory": "01八字命理",
                "sourceFile": source_file,
                "tier": item["tier"],
                "topicsAttempted": item["topicsAttempted"],
            }
        )

    payload = {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "filesTotal": len(normalized),
        "byTier": {},
        "files": normalized,
    }
    for tier in ("T1", "T2", "T3", "T4"):
        payload["byTier"][tier] = sum(1 for f in normalized if f["tier"] == tier)

    manifest_files = [build_file_manifest(f["sourceFile"]) for f in normalized]
    by_authority: dict[str, int] = {}
    by_library: dict[str, int] = {}
    for row in manifest_files:
        at = row.get("authorityTier", "?")
        lr = row.get("libraryRole", "?")
        by_authority[at] = by_authority.get(at, 0) + 1
        by_library[lr] = by_library.get(lr, 0) + 1

    manifest_payload = {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "filesTotal": len(manifest_files),
        "byAuthorityTier": by_authority,
        "byLibraryRole": by_library,
        "files": manifest_files,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    MANIFEST_OUTPUT.write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest_payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
