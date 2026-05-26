"""Add searchable OCR text layer to scanned PDFs using RapidOCR + PyMuPDF."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import fitz
from rapidocr_onnxruntime import RapidOCR


ROOT = Path(r"d:\ZY")
PROGRESS_FILE = ROOT / "code" / "tmp" / "ocr_progress.json"
OCR_DPI = 120
CHECKPOINT_EVERY = 5


def persist_doc(doc: fitz.Document, dst: Path, opened_from_output: bool) -> tuple[fitz.Document, bool]:
    if opened_from_output:
        doc.saveIncr()
    else:
        doc.save(dst)
    doc.close()
    return fitz.open(dst), True


def find_pdfs() -> list[Path]:
    pdfs: list[Path] = []
    for folder in ROOT.rglob("*"):
        if not folder.is_dir():
            continue
    for path in ROOT.rglob("*.pdf"):
        if path.parent.name == "八字" and "图解子平真诠" in path.name:
            if "-ocr" not in path.stem:
                pdfs.append(path)
    pdfs.sort(key=lambda p: p.name)
    return pdfs


def output_path(src: Path) -> Path:
    out_dir = src.parent / "ocr"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{src.stem}-ocr.pdf"


def write_progress(payload: dict) -> None:
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def add_ocr_layer(src: Path, dst: Path, ocr: RapidOCR) -> dict:
    scale = OCR_DPI / 72.0
    matrix = fitz.Matrix(scale, scale)

    opened_from_output = False
    if dst.exists():
        doc = fitz.open(dst)
        start_page = len(doc)
        opened_from_output = True
        src_doc = fitz.open(src)
        if start_page >= len(src_doc):
            src_doc.close()
            doc.close()
            return {"status": "already_done", "pages": start_page}
        src_doc.close()
    else:
        doc = fitz.open()
        start_page = 0

    src_doc = fitz.open(src)
    total_pages = len(src_doc)
    total_chars = 0
    started = time.time()

    for page_index in range(start_page, total_pages):
        page_started = time.time()
        src_page = src_doc[page_index]

        if page_index < len(doc):
            out_page = doc[page_index]
        else:
            out_page = doc.new_page(width=src_page.rect.width, height=src_page.rect.height)
            out_page.show_pdf_page(out_page.rect, src_doc, page_index)

        pix = src_page.get_pixmap(matrix=matrix, alpha=False)
        img_bytes = pix.tobytes("png")
        results, _ = ocr(img_bytes)

        page_chars = 0
        for item in results or []:
            box, text, _score = item
            text = (text or "").strip()
            if not text:
                continue
            xs = [point[0] for point in box]
            ys = [point[1] for point in box]
            x0 = min(xs) / scale
            y0 = min(ys) / scale
            x1 = max(xs) / scale
            y1 = max(ys) / scale
            rect = fitz.Rect(x0, y0, x1, y1)
            if rect.width <= 0 or rect.height <= 0:
                continue
            fontsize = max(4.0, min((y1 - y0) * 0.85, 24.0))
            out_page.insert_text((x0, y0), text, fontsize=fontsize, render_mode=3)
            page_chars += len(text)

        total_chars += page_chars

        is_checkpoint = (page_index + 1) % CHECKPOINT_EVERY == 0
        is_last_page = page_index == total_pages - 1
        if is_checkpoint or is_last_page:
            doc, opened_from_output = persist_doc(doc, dst, opened_from_output)

        elapsed = time.time() - started
        avg = elapsed / (page_index - start_page + 1)
        remaining = avg * (total_pages - page_index - 1)
        write_progress(
            {
                "status": "running",
                "file": str(src),
                "output": str(dst),
                "current_page": page_index + 1,
                "total_pages": total_pages,
                "page_seconds": round(time.time() - page_started, 2),
                "page_chars": page_chars,
                "total_chars": total_chars,
                "elapsed_seconds": round(elapsed, 1),
                "eta_seconds": round(remaining, 1),
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    src_doc.close()
    if len(doc) > 0:
        if opened_from_output:
            doc.saveIncr()
        else:
            doc.save(dst, garbage=4, deflate=True)
    doc.close()

    return {
        "status": "done",
        "file": str(src),
        "output": str(dst),
        "pages": total_pages,
        "total_chars": total_chars,
        "elapsed_seconds": round(time.time() - started, 1),
    }


def main() -> int:
    targets = find_pdfs()
    if not targets:
        write_progress({"status": "error", "message": "no target pdfs found"})
        return 1

    ocr = RapidOCR()
    results: list[dict] = []
    overall_started = time.time()

    write_progress(
        {
            "status": "starting",
            "files": [str(p) for p in targets],
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    for index, src in enumerate(targets, start=1):
        dst = output_path(src)
        write_progress(
            {
                "status": "file_start",
                "file_index": index,
                "file_total": len(targets),
                "file": str(src),
                "output": str(dst),
            }
        )
        result = add_ocr_layer(src, dst, ocr)
        result["file_index"] = index
        results.append(result)

    write_progress(
        {
            "status": "completed",
            "results": results,
            "elapsed_seconds": round(time.time() - overall_started, 1),
            "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    print(json.dumps({"status": "completed", "results": results}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
