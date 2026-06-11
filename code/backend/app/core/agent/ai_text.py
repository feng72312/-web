from __future__ import annotations

import re

# Strip model footers / disclaimers from LLM output before sending to clients.
_FOOTER_LINE_RE = re.compile(
    r"(以上内容由|以上推算由|由\s*.+\s*生成|由AI生成|DeepSeek|deepseek|ChatGPT|OpenAI|Claude|"
    r"Composer|仅供娱乐|娱乐参考|仅供参考|玄学虽有趣|生活更值得用心|愿你在现实中)",
    re.IGNORECASE,
)


def sanitize_ai_text(text: str) -> str:
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
