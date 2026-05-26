from __future__ import annotations


def split_paragraphs(text: str) -> list[str]:
    parts = [part.strip() for part in text.split("\n\n") if part.strip()]
    if parts:
        return parts
    return [text.strip()] if text.strip() else []


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
