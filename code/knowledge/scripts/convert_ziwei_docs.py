"""Convert 11紫微斗数 .doc files to UTF-8 .txt and archive originals."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "数据库" / "11紫微斗数"
REPORT = ROOT / "report" / "紫薇斗数最强方案" / "doc_to_txt_report.json"
sys.path.insert(0, str(ROOT / "code" / "rag"))
sys.path.insert(0, str(ROOT / "code" / "knowledge" / "scripts"))

from decrypt_sources import run_decrypt
from doc_reader import normalize_text, read_document

WD_FORMAT_TEXT = 2
WD_ENCODING_UTF8 = 65001


def _write_txt(out: Path, text: str) -> bool:
    cleaned = normalize_text(text)
    if len(cleaned.strip()) < 32:
        return False
    out.write_text(cleaned, encoding="utf-8")
    return out.is_file() and out.stat().st_size > 32


def _convert_via_reader(path: Path, out: Path) -> tuple[str, str]:
    try:
        text = read_document(path)
        if _write_txt(out, text):
            return "ok", "read_document"
        return "fail", "empty_after_read"
    except Exception as exc:
        return "fail", f"read_document: {exc}"[:120]


def _convert_via_word(path: Path, out: Path, *, repair: bool = False) -> tuple[str, str]:
    import win32com.client

    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        open_kwargs = {
            "FileName": str(path.resolve()),
            "ConfirmConversions": True,
            "ReadOnly": True,
            "AddToRecentFiles": False,
        }
        if repair:
            open_kwargs["OpenAndRepair"] = True
        doc = word.Documents.Open(**open_kwargs)
        doc.SaveAs2(
            str(out.resolve()),
            FileFormat=WD_FORMAT_TEXT,
            Encoding=WD_ENCODING_UTF8,
        )
        doc.Close(False)
        word.Quit()
        if out.is_file() and out.stat().st_size > 32:
            return "ok", "word_saveas"
        return "fail", "empty_output"
    except Exception as exc:
        if doc is not None:
            try:
                doc.Close(False)
            except Exception:
                pass
        if word is not None:
            try:
                word.Quit()
            except Exception:
                pass
        return "fail", str(exc)[:120]


def _convert_via_wps(path: Path, out: Path) -> tuple[str, str]:
    import win32com.client

    for app_name in ("Kwps.Application", "Wps.Application"):
        app = None
        doc = None
        try:
            app = win32com.client.DispatchEx(app_name)
            app.Visible = False
            doc = app.Documents.Open(str(path.resolve()), ReadOnly=True)
            doc.SaveAs2(str(out.resolve()), FileFormat=WD_FORMAT_TEXT)
            doc.Close(False)
            app.Quit()
            if out.is_file() and out.stat().st_size > 32:
                return "ok", f"{app_name}_saveas"
        except Exception:
            if doc is not None:
                try:
                    doc.Close(False)
                except Exception:
                    pass
            if app is not None:
                try:
                    app.Quit()
                except Exception:
                    pass
    return "fail", "wps_unavailable"


def convert_one(path: Path, *, archive_dir: Path) -> dict:
    rel = str(path.relative_to(SOURCE)).replace("\\", "/")
    if path.name.startswith("~$"):
        return {"file": rel, "status": "skip", "detail": "temp_file"}

    stem = path.name
    if stem.endswith(".txt.doc"):
        stem = stem[: -len(".doc")]
    out = path.with_name(Path(stem).with_suffix(".txt").name)

    if out.is_file() and out.stat().st_size > 32:
        status, detail = "skip", "txt_exists"
    else:
        status, detail = _convert_via_reader(path, out)
        if status != "ok":
            status, detail = _convert_via_word(path, out, repair=False)
        if status != "ok":
            status, detail = _convert_via_word(path, out, repair=True)
        if status != "ok":
            status, detail = _convert_via_wps(path, out)

    archived = False
    if status in {"ok", "skip"} and out.is_file():
        archive_dir.mkdir(parents=True, exist_ok=True)
        target = archive_dir / path.name
        if path.is_file():
            if target.exists():
                target.unlink()
            shutil.move(str(path), str(target))
            archived = True

    return {
        "file": rel,
        "txt": str(out.relative_to(SOURCE)).replace("\\", "/"),
        "status": status,
        "detail": detail,
        "archivedDoc": archived,
        "txtBytes": out.stat().st_size if out.is_file() else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(SOURCE))
    parser.add_argument("--decrypt", action="store_true", default=True)
    parser.add_argument("--no-decrypt", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    source = Path(args.source)
    if not source.is_dir():
        print(f"source not found: {source}")
        return 1

    if args.decrypt and not args.no_decrypt and not args.dry_run:
        code = run_decrypt([source])
        if code != 0:
            print(f"[warn] decrypt exited with code {code}")

    archive_dir = source / "_doc_backup"
    results: list[dict] = []
    for path in sorted(source.rglob("*.doc")):
        if "_doc_backup" in path.parts:
            continue
        if args.dry_run:
            results.append({"file": str(path.relative_to(source)), "status": "dry_run"})
            continue
        row = convert_one(path, archive_dir=archive_dir)
        results.append(row)
        print(f"[{row['status']}] {row['file']} -> {row.get('txt', '')} ({row.get('detail', '')})")

    ok = sum(1 for row in results if row.get("status") == "ok")
    skip = sum(1 for row in results if row.get("status") == "skip")
    fail = sum(1 for row in results if row.get("status") == "fail")
    payload = {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "source": str(source),
        "ok": ok,
        "skip": skip,
        "fail": fail,
        "results": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary ok={ok} skip={skip} fail={fail}")
    print(f"report {REPORT}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
