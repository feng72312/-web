from __future__ import annotations


def strip_stance_line(text: str) -> str:
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("倾向:")]
    return "\n".join(lines).strip() or text.strip()


def extract_stance_from_summary(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("倾向:"):
            return stripped.replace("倾向:", "", 1).strip() or "未定"
    return "未定"
