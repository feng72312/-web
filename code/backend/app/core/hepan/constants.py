from __future__ import annotations

from app.core.hepan.models import HepanScene

GAN_WUXING: dict[str, str] = {
    "\u7532": "\u6728",
    "\u4e59": "\u6728",
    "\u4e19": "\u706b",
    "\u4e01": "\u706b",
    "\u620a": "\u571f",
    "\u5df1": "\u571f",
    "\u5e9a": "\u91d1",
    "\u8f9b": "\u91d1",
    "\u58ec": "\u6c34",
    "\u7678": "\u6c34",
}

WUXING_SHENG: dict[str, str] = {
    "\u6728": "\u706b",
    "\u706b": "\u571f",
    "\u571f": "\u91d1",
    "\u91d1": "\u6c34",
    "\u6c34": "\u6728",
}

WUXING_KE: dict[str, str] = {
    "\u6728": "\u571f",
    "\u571f": "\u6c34",
    "\u6c34": "\u706b",
    "\u706b": "\u91d1",
    "\u91d1": "\u6728",
}

# gender 1=male -> 财; 0=female -> 官
SPOUSE_SHISHEN: dict[int, tuple[str, ...]] = {
    1: ("\u6b63\u8d22", "\u504f\u8d22"),
    0: ("\u6b63\u5b98", "\u4e03\u6740"),
}

SHA_STAR_NAMES: frozenset[str] = frozenset(
    {
        "\u64ce\u7f8a",
        "\u9640\u7f57",
        "\u706b\u661f",
        "\u94c3\u661f",
        "\u5730\u7a7a",
        "\u5730\u52ab",
        "\u5929\u5211",
    }
)

ROMANCE_PALACE_PAIRS: list[tuple[str, str]] = [
    ("\u592b\u59bb", "\u547d\u5bab"),
    ("\u547d\u5bab", "\u592b\u59bb"),
    ("\u592b\u59bb", "\u798f\u5fb7"),
]

PARTNERSHIP_PALACE_PAIRS: list[tuple[str, str]] = [
    ("\u5b98\u7984", "\u5b98\u7984"),
    ("\u8d22\u535a", "\u8d22\u535a"),
    ("\u4ea4\u53cb", "\u4ea4\u53cb"),
    ("\u547d\u5bab", "\u547d\u5bab"),
]

SCENE_PALACE_PAIRS: dict[HepanScene, list[tuple[str, str]]] = {
    "romance": ROMANCE_PALACE_PAIRS,
    "marriage": ROMANCE_PALACE_PAIRS,
    "partnership": PARTNERSHIP_PALACE_PAIRS,
}

PILLAR_KEYS = ("year", "month", "day", "hour")
