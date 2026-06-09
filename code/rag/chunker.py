from __future__ import annotations

import re
from dataclasses import dataclass

CHAPTER_PATTERNS = (
    re.compile(r"^第[一二三四五六七八九十百千零〇\d]+[章节卷篇回]"),
    re.compile(r"^[卷帙][一二三四五六七八九十百千零〇\d]+"),
    re.compile(r"^[一二三四五六七八九十百千零〇]+[、\.．]"),
    re.compile(r"^（[一二三四五六七八九十]+）"),
    re.compile(r"^\d+[、\.．]\s*\S"),
)


@dataclass
class TextChunk:
    text: str
    chapter: str = ""


def split_paragraphs(text: str) -> list[str]:
    parts = [part.strip() for part in text.split("\n\n") if part.strip()]
    if parts:
        return parts
    return [text.strip()] if text.strip() else []


def is_chapter_heading(line: str) -> bool:
    candidate = line.strip()
    if not candidate or len(candidate) > 48:
        return False
    return any(pattern.match(candidate) for pattern in CHAPTER_PATTERNS)


def split_sections(text: str) -> list[tuple[str, str]]:
    lines = text.split("\n")
    sections: list[tuple[str, str]] = []
    current_chapter = ""
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if is_chapter_heading(stripped):
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append((current_chapter, body))
            current_chapter = stripped
            current_lines = []
            continue
        current_lines.append(line)

    if current_lines:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_chapter, body))

    if sections:
        return sections
    cleaned = text.strip()
    return [("", cleaned)] if cleaned else []


def chunk_text(
    text: str,
    chunk_size: int = 400,
    overlap: int = 80,
) -> list[str]:
    paragraphs = split_paragraphs(text)
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = paragraph
            continue

        if current:
            chunks.append(current)
            current = ""

        start = 0
        while start < len(paragraph):
            end = min(start + chunk_size, len(paragraph))
            chunks.append(paragraph[start:end])
            if end >= len(paragraph):
                break
            start = max(end - overlap, start + 1)

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def chunk_document(
    text: str,
    chunk_size: int = 400,
    overlap: int = 80,
) -> list[TextChunk]:
    """Chapter-aware chunking: split by headings first, then paragraph chunking."""
    sections = split_sections(text)
    output: list[TextChunk] = []
    for chapter, section_text in sections:
        for chunk in chunk_text(section_text, chunk_size, overlap):
            output.append(TextChunk(text=chunk, chapter=chapter))
    return output
