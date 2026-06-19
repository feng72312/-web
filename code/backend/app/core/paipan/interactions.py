from __future__ import annotations

PILLAR_KEYS = ("year", "month", "day", "hour")

GAN_HE = [
    ("\u7532", "\u5df1"),
    ("\u4e59", "\u5e9a"),
    ("\u4e19", "\u8f9b"),
    ("\u4e01", "\u58ec"),
    ("\u620a", "\u7678"),
]

ZHI_CHONG = [
    ("\u5b50", "\u5348"),
    ("\u4e11", "\u672a"),
    ("\u5bc5", "\u7533"),
    ("\u536f", "\u9149"),
    ("\u8fb0", "\u620c"),
    ("\u5df3", "\u4ea5"),
]

ZHI_HE = [
    ("\u5b50", "\u4e11"),
    ("\u5bc5", "\u4ea5"),
    ("\u536f", "\u620c"),
    ("\u8fb0", "\u9149"),
    ("\u5df3", "\u7533"),
    ("\u5348", "\u672a"),
]

ZHI_HAI = [
    ("\u5b50", "\u672a"),
    ("\u4e11", "\u5348"),
    ("\u5bc5", "\u5df3"),
    ("\u536f", "\u8fb0"),
    ("\u7533", "\u5bc5"),
    ("\u9149", "\u620c"),
    ("\u620c", "\u9149"),
    ("\u4ea5", "\u5df3"),
]

ZHI_XING = [
    ("\u5b50", "\u536f"),
    ("\u4e11", "\u672a"),
    ("\u4e11", "\u620c"),
    ("\u620c", "\u672a"),
    ("\u5bc5", "\u5df3"),
    ("\u5df3", "\u7533"),
    ("\u7533", "\u5bc5"),
]


def _find_pairs(items: dict[str, str], pairs: list[tuple[str, str]], label: str) -> list[str]:
    values = list(items.values())
    notes: list[str] = []
    for a, b in pairs:
        if a in values and b in values:
            notes.append(f"{a}{b}{label}")
    return notes


def build_interaction_notes(pillars: dict[str, dict]) -> dict[str, str]:
    gans = {key: pillars[key]["gan"] for key in PILLAR_KEYS}
    zhis = {key: pillars[key]["zhi"] for key in PILLAR_KEYS}
    stem_notes = _find_pairs(gans, GAN_HE, "\u5408")
    branch_notes = []
    branch_notes.extend(_find_pairs(zhis, ZHI_CHONG, "\u51b2"))
    branch_notes.extend(_find_pairs(zhis, ZHI_HE, "\u5408"))
    branch_notes.extend(_find_pairs(zhis, ZHI_HAI, "\u5bb3"))
    branch_notes.extend(_find_pairs(zhis, ZHI_XING, "\u5211"))
    return {
        "stemNotes": "\u3001".join(stem_notes) if stem_notes else "\u6682\u65e0",
        "branchNotes": "\u3001".join(branch_notes) if branch_notes else "\u6682\u65e0",
    }
