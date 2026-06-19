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


TOC_LINE_RE = re.compile(r"[.．…]{4,}")
CASE_HEAD_RE = re.compile(r"(乾造|坤造|命例|案例|卦例|占例|问[:：])")
LIUYAO_CASE_RE = re.compile(r"(占得|问求财|问官|占病|占婚|验[:：])")
ANNOTATION_RE = re.compile(r"(注[:：]|注解|按[:：]|评曰|原注)")
EDITOR_RE = re.compile(r"(编者|责任编辑|www\.|TXT小说库|虚拟宝库)")


def infer_text_role(text: str, chapter: str = "") -> str:
    sample = f"{chapter}\n{text[:320]}".strip()
    if not sample:
        return "original"
    if "目录" in sample[:120] or TOC_LINE_RE.search(sample[:320]):
        return "toc"
    if CASE_HEAD_RE.search(sample[:160]) or LIUYAO_CASE_RE.search(sample[:200]):
        return "case"
    if EDITOR_RE.search(sample[:160]):
        return "editor_note"
    if ANNOTATION_RE.search(sample[:240]):
        return "annotation"
    if chapter and re.search(r"(疏|解|释义)", chapter):
        return "commentary"
    return "original"


def infer_case_only(text_role: str, judgment_policy: str = "") -> str:
    if text_role == "case":
        return "1"
    if judgment_policy in {"case_only_no_judge", "explain_only"}:
        return "0"
    return "0"


def infer_topic_scope_hint(text: str, chapter: str = "", file_topics: list[str] | None = None) -> str:
    sample = f"{chapter}\n{text[:240]}"
    hints: list[str] = []
    mapping = (
        ("用神", "yong_shen"),
        ("旺衰", "wang_shuai"),
        ("月建", "wang_shuai"),
        ("日辰", "wang_shuai"),
        ("旬空", "xun_kong"),
        ("月破", "yue_po"),
        ("飞伏", "fei_fu"),
        ("反吟", "dong_bian"),
        ("伏吟", "dong_bian"),
        ("应期", "ying_qi"),
        ("世应", "shi_ying"),
        ("动爻", "dong_bian"),
        ("装卦", "casting"),
        ("纳甲", "casting"),
        ("求财", "topic_divination"),
        ("功名", "topic_divination"),
        ("婚姻", "topic_divination"),
        ("占病", "topic_divination"),
        ("四化", "mutagen"),
        ("化禄", "mutagen"),
        ("化忌", "mutagen"),
        ("飞星", "mutagen"),
        ("大限", "limit"),
        ("流年", "limit"),
        ("命宫", "palace"),
        ("夫妻", "palace"),
        ("官禄", "palace"),
        ("财帛", "palace"),
        ("格局", "pattern"),
        ("庙旺", "star"),
        ("主星", "star"),
    )
    for keyword, topic in mapping:
        if keyword in sample and topic not in hints:
            hints.append(topic)
    if file_topics:
        for topic in file_topics:
            if topic not in hints:
                hints.append(topic)
    if not hints:
        hints.append("general")
    return ",".join(hints[:6])


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
