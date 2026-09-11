from __future__ import annotations

import re

# Strip model footers / disclaimers from LLM output before sending to clients.
_FOOTER_LINE_RE = re.compile(
    r"(以上内容由|以上推算由|由\s*.+\s*生成|由AI生成|DeepSeek|deepseek|ChatGPT|OpenAI|Claude|"
    r"Composer|仅供娱乐|娱乐参考|仅供参考|玄学虽有趣|生活更值得用心|愿你在现实中)",
    re.IGNORECASE,
)
_MODE_LINE_RE = re.compile(r"^\s*\[MODE:\s*[A-Z][A-Z0-9_-]*\s*\]\s*$")
_META_RESEARCH_RE = re.compile(
    r"(结合上文命盘|相关资料里查找|人物包与相关资料|我先在.+查找)"
)
_INCOMPLETE_META_PREFIX_RE = re.compile(r"^(你问的是|我先在|要求结合上文)")


def strip_agent_protocol(text: str) -> str:
    if not text:
        return ""
    kept = [line for line in text.splitlines() if not _MODE_LINE_RE.match(line)]
    index = 0
    while index < len(kept):
        line = kept[index].strip()
        if not line:
            index += 1
            continue
        if _META_RESEARCH_RE.search(line):
            index += 1
            continue
        break
    return "\n".join(kept[index:]).strip()


def visible_stream_text(raw: str) -> str:
    cleaned = strip_agent_protocol(raw)
    if not cleaned:
        return ""
    if "\n\n" not in raw.strip() and _INCOMPLETE_META_PREFIX_RE.match(cleaned):
        return ""
    return cleaned


def sanitize_ai_text(text: str) -> str:
    if not text:
        return ""
    text = strip_agent_protocol(text)
    if not text:
        return ""
    lines = text.splitlines()
    end = len(lines)
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped in ("---", "***", "___", "----"):
            end = min(end, index)
            continue
        if _FOOTER_LINE_RE.search(stripped):
            end = min(end, index)
    body = "\n".join(lines[:end]).strip()
    body = re.sub(r"\n-{3,}\s*$", "", body)
    return body.strip()
