"""Move 01八字命理 source files into folders by authority classification."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
SOURCE_01 = ROOT / "数据库" / "01八字命理"
MANIFEST_PATH = KNOWLEDGE_DIR / "data" / "sources" / "bazi_sources_manifest.json"
REPORT_PATH = ROOT / "report" / "八字判盘最强方案" / "01八字命理文件整理记录.json"

TARGET_DIRS = {
    "S": "S_主裁经典",
    "A": "A_辅助经典",
    "B": "B_现代解释",
    "C": "C_命例经验",
    "D": "D_低信排除",
}

ALLOWED_SUFFIXES = {".txt", ".doc", ".docx"}


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _find_current_file(source_file: str) -> Path | None:
    rel = Path(source_file)
    direct = SOURCE_01 / rel
    if direct.is_file():
        return direct
    candidates = [p for p in SOURCE_01.rglob(rel.name) if p.is_file()]
    return candidates[0] if candidates else None


def organize(*, dry_run: bool = False) -> dict:
    payload = _load_manifest()
    moved: list[dict] = []
    skipped: list[dict] = []
    missing: list[dict] = []

    for row in payload.get("files") or []:
        source_file = str(row.get("sourceFile") or "")
        authority = str(row.get("authorityTier") or "D")
        target_dir_name = TARGET_DIRS.get(authority, TARGET_DIRS["D"])
        current = _find_current_file(source_file)
        if current is None:
            missing.append({"sourceFile": source_file, "authorityTier": authority})
            continue
        if current.suffix.lower() not in ALLOWED_SUFFIXES:
            skipped.append({"sourceFile": source_file, "reason": "unsupported suffix"})
            continue

        target_dir = SOURCE_01 / target_dir_name
        target = target_dir / current.name
        if current.resolve() == target.resolve():
            skipped.append({"sourceFile": source_file, "reason": "already organized"})
            continue
        if target.exists():
            raise FileExistsError(f"target exists: {target}")

        moved.append(
            {
                "sourceFile": source_file,
                "from": str(current),
                "to": str(target),
                "authorityTier": authority,
                "libraryRole": row.get("libraryRole", ""),
                "evidenceRole": row.get("evidenceRole", ""),
            }
        )
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current), str(target))

    result = {
        "organizedAt": datetime.now().isoformat(timespec="seconds"),
        "dryRun": dry_run,
        "movedCount": len(moved),
        "skippedCount": len(skipped),
        "missingCount": len(missing),
        "targetDirs": TARGET_DIRS,
        "moved": moved,
        "skipped": skipped,
        "missing": missing,
    }
    if not dry_run:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = organize(dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["missingCount"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
