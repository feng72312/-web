"""Validate OCR PDFs and write ingest manifest after OCR completes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import fitz

ROOT = Path(r"d:\ZY")
PROGRESS_FILE = ROOT / "code" / "tmp" / "ocr_progress.json"
MANIFEST_FILE = ROOT / "code" / "tmp" / "ocr_manifest.json"


def main() -> int:
    ocr_dir = ROOT / "数据库" / "八字" / "ocr"
    outputs = sorted(ocr_dir.glob("*-ocr.pdf"))
    if not outputs:
        payload = {"status": "error", "message": "no ocr pdf outputs found"}
        MANIFEST_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    files: list[dict] = []
    for path in outputs:
        doc = fitz.open(path)
        chars = sum(len(doc[i].get_text().strip()) for i in range(len(doc)))
        files.append(
            {
                "path": str(path),
                "pages": len(doc),
                "chars": chars,
            }
        )
        doc.close()

    payload = {
        "status": "ready",
        "files": files,
        "ingest_paths": [item["path"] for item in files],
    }
    MANIFEST_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
