from __future__ import annotations

from pathlib import Path


def parse_filename(filename: str) -> dict[str, str]:
    """Parse book filename like 滴天髓阐微-清-任铁樵.txt into metadata."""
    stem = Path(filename).stem.replace("·", "-").replace("．", ".")
    parts = [part.strip() for part in stem.split("-") if part.strip()]

    if len(parts) >= 3:
        return {
            "classic": parts[0],
            "dynasty": parts[1],
            "author": "-".join(parts[2:]),
        }
    if len(parts) == 2:
        return {
            "classic": parts[0],
            "dynasty": parts[1],
            "author": "",
        }
    return {
        "classic": stem,
        "dynasty": "",
        "author": "",
    }
