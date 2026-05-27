from __future__ import annotations

import re
from pathlib import Path


def read_txt(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "gbk"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def read_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(parts)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u000b", "\n").replace("\xa0", " ")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_doc_win32(path: Path) -> str:
    import win32com.client

    app_names = ("Word.Application", "Kwps.Application", "Wps.Application")
    last_error: Exception | None = None

    for app_name in app_names:
        word = None
        doc = None
        try:
            word = win32com.client.DispatchEx(app_name)
            word.Visible = False
            word.DisplayAlerts = 0
            doc = word.Documents.Open(str(path.resolve()), ReadOnly=True)
            text = str(doc.Content.Text)
            doc.Close(False)
            word.Quit()
            return text
        except Exception as exc:
            last_error = exc
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

    raise RuntimeError(f"cannot read doc file: {path.name}") from last_error


def read_doc_batch(paths: list[Path], batch_size: int = 8) -> dict[Path, str]:
    if not paths:
        return {}

    results: dict[Path, str] = {}
    for start in range(0, len(paths), batch_size):
        batch = paths[start : start + batch_size]
        for path in batch:
            print(f"[doc] reading {path.name} ...", flush=True)
        batch_results = _read_doc_batch_once(batch)
        results.update(batch_results)
    return results


def _read_doc_batch_once(paths: list[Path]) -> dict[Path, str]:
    if not paths:
        return {}

    import win32com.client

    app_names = ("Word.Application", "Kwps.Application", "Wps.Application")
    last_error: Exception | None = None

    for app_name in app_names:
        word = None
        opened: list[tuple[Path, object]] = []
        results: dict[Path, str] = {}
        try:
            word = win32com.client.DispatchEx(app_name)
            word.Visible = False
            word.DisplayAlerts = 0

            for path in paths:
                doc = word.Documents.Open(str(path.resolve()), ReadOnly=True)
                opened.append((path, doc))
                results[path] = str(doc.Content.Text)
                doc.Close(False)
                opened.clear()

            word.Quit()
            return results
        except Exception as exc:
            last_error = exc
            for _, doc in opened:
                try:
                    doc.Close(False)
                except Exception:
                    pass
            if word is not None:
                try:
                    word.Quit()
                except Exception:
                    pass

    raise RuntimeError("cannot read doc files in batch") from last_error


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        raw = read_txt(path)
    elif suffix == ".docx":
        raw = read_docx(path)
    elif suffix == ".doc":
        raw = read_doc_win32(path)
    else:
        raise ValueError(f"unsupported file type: {path.suffix}")

    text = normalize_text(raw)
    if not text:
        raise ValueError(f"empty document: {path.name}")
    return text
