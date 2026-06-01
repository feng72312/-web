from __future__ import annotations


def strip_stance_line(text: str) -> str:
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("倾向:")]
    return "\n".join(lines).strip() or text.strip()
