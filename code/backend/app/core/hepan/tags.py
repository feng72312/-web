from __future__ import annotations


def build_summary_tags(notes: list[dict], limit: int = 6) -> list[str]:
    priority = {"fit": 0, "caution": 1, "neutral": 2}
    sorted_notes = sorted(
        notes,
        key=lambda n: (priority.get(n.get("level", "neutral"), 9), n.get("id", "")),
    )
    tags: list[str] = []
    seen: set[str] = set()
    for note in sorted_notes:
        title = (note.get("title") or "").strip()
        if not title or title in seen:
            continue
        seen.add(title)
        tags.append(title)
        if len(tags) >= limit:
            break
    return tags
