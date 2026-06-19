from __future__ import annotations

from typing import Any

from app.core.paipan.engine import PaipanEngine
from app.core.paipan.models import PaipanInput
from app.core.utils.shuowen_index import lookup_chars

WUXING_KEYS = ("木", "火", "土", "金", "水")

WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
WUXING_BEI_SHENG = {v: k for k, v in WUXING_SHENG.items()}

RADICAL_WUXING: dict[str, str] = {
    "木": "木",
    "艸": "木",
    "艹": "木",
    "竹": "木",
    "火": "火",
    "灬": "火",
    "土": "土",
    "山": "土",
    "石": "土",
    "田": "土",
    "阜": "土",
    "金": "金",
    "釒": "金",
    "水": "水",
    "氵": "水",
    "冫": "水",
    "雨": "水",
    "魚": "水",
}

LUCKY_NUMBERS = frozenset(
    {
        1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 31, 32,
        33, 35, 37, 39, 41, 45, 47, 48, 51, 52, 57, 61, 63, 65, 67, 68, 81,
    }
)


def _load_strokes() -> dict[str, int]:
    import json

    from app.core.utils.data_paths import utils_data_dir

    path = utils_data_dir() / "naming_strokes.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def stroke_of(char: str, overrides: dict[str, int] | None = None) -> int | None:
    table = _load_strokes()
    if overrides and char in overrides:
        return int(overrides[char])
    value = table.get(char)
    return int(value) if value else None


def radical_wuxing(radical: str) -> str:
    radical = (radical or "").strip()
    if not radical:
        return ""
    if radical in RADICAL_WUXING:
        return RADICAL_WUXING[radical]
    first = radical[0]
    return RADICAL_WUXING.get(first, "")


def shuli_wuxing(number: int) -> str:
    if number <= 0:
        return ""
    tail = number % 10
    if tail in (1, 2):
        return "木"
    if tail in (3, 4):
        return "火"
    if tail in (5, 6):
        return "土"
    if tail in (7, 8):
        return "金"
    return "水"


def shuli_luck(number: int) -> str:
    if number <= 0:
        return "unknown"
    if number in LUCKY_NUMBERS:
        return "吉"
    if number in {2, 4, 9, 10, 12, 14, 19, 20, 22, 26, 27, 28, 30, 34, 36, 38, 40, 42, 43, 44, 46, 49, 50, 53, 54, 56, 58, 59, 60, 62, 64, 66, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80}:
        return "凶"
    return "平"


def compute_wuge(
    surname: str,
    given_name: str,
    *,
    stroke_overrides: dict[str, int] | None = None,
) -> dict[str, Any]:
    surname = surname.strip()
    given_name = given_name.strip()
    s_chars = [ch for ch in surname if "\u4e00" <= ch <= "\u9fff"]
    g_chars = [ch for ch in given_name if "\u4e00" <= ch <= "\u9fff"]
    if not s_chars:
        raise ValueError("surname required")

    missing: list[str] = []
    s_strokes = []
    for ch in s_chars:
        count = stroke_of(ch, stroke_overrides)
        if count is None:
            missing.append(ch)
            count = 0
        s_strokes.append(count)

    g_strokes = []
    for ch in g_chars:
        count = stroke_of(ch, stroke_overrides)
        if count is None:
            missing.append(ch)
            count = 0
        g_strokes.append(count)

    if len(s_chars) == 1:
        tiange = s_strokes[0] + 1
    else:
        tiange = sum(s_strokes)

    if g_chars:
        renge = s_strokes[-1] + g_strokes[0]
        dige = sum(g_strokes)
    else:
        renge = s_strokes[-1] + 1
        dige = 1

    zongge = sum(s_strokes) + sum(g_strokes)
    if len(s_chars) == 1 and len(g_chars) == 1:
        waige = 2
    else:
        waige = zongge - renge + 1

    grids = {
        "天格": tiange,
        "人格": renge,
        "地格": dige,
        "外格": waige,
        "总格": zongge,
    }
    details = []
    for name, value in grids.items():
        details.append(
            {
                "grid": name,
                "strokes": value,
                "wuxing": shuli_wuxing(value),
                "luck": shuli_luck(value),
            }
        )

    return {
        "surname": surname,
        "givenName": given_name,
        "charStrokes": [
            {"char": ch, "strokes": stroke_of(ch, stroke_overrides) or 0}
            for ch in s_chars + g_chars
        ],
        "grids": details,
        "missingStrokeChars": missing,
    }


def favored_wuxing_from_chart(chart: dict[str, Any]) -> dict[str, Any]:
    counts = chart.get("wuxingCount") or {}
    dm_wx = chart.get("dayMasterWuxing") or ""
    items = [(wx, counts.get(wx, 0)) for wx in WUXING_KEYS]
    weakest = min(items, key=lambda row: row[1])[0]
    strongest = max(items, key=lambda row: row[1])[0]

    dm_count = counts.get(dm_wx, 0)
    total = sum(counts.values()) or 1
    dm_ratio = dm_count / total
    if dm_ratio >= 0.35:
        strength = "偏强"
        favor = [WUXING_SHENG[dm_wx], WUXING_KE[dm_wx]]
    elif dm_ratio <= 0.15:
        strength = "偏弱"
        favor = [WUXING_BEI_SHENG.get(dm_wx, ""), dm_wx]
    else:
        strength = "中和"
        favor = [weakest, WUXING_BEI_SHENG.get(weakest, "")]

    favor = [wx for wx in favor if wx]
    favor.append(weakest)
    seen: set[str] = set()
    ordered: list[str] = []
    for wx in favor:
        if wx and wx not in seen:
            seen.add(wx)
            ordered.append(wx)

    return {
        "dayMasterWuxing": dm_wx,
        "strength": strength,
        "weakest": weakest,
        "strongest": strongest,
        "favoredWuxing": ordered,
        "avoidWuxing": [strongest] if strongest != weakest else [],
    }


def analyze_name(
    *,
    surname: str,
    given_name: str = "",
    stroke_overrides: dict[str, int] | None = None,
    birth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    surname = surname.strip()
    given_name = given_name.strip()
    if not surname:
        raise ValueError("surname required")

    full_name = surname + given_name
    shuowen = lookup_chars(full_name)
    char_wuxing = []
    for row in shuowen:
        wx = radical_wuxing(str(row.get("radical", "")))
        char_wuxing.append({"char": row.get("char", ""), "radicalWuxing": wx, "radical": row.get("radical", "")})

    wuge = compute_wuge(surname, given_name, stroke_overrides=stroke_overrides)

    bazi_profile = None
    chart = None
    if birth:
        engine = PaipanEngine()
        chart_input = PaipanInput(
            name=full_name,
            calendar_type=birth.get("calendarType", "solar"),
            year=int(birth["year"]),
            month=int(birth["month"]),
            day=int(birth["day"]),
            hour=int(birth.get("hour", 12)),
            minute=int(birth.get("minute", 0)),
            second=int(birth.get("second", 0)),
            gender=int(birth.get("gender", 1)),
            is_leap_month=bool(birth.get("isLeapMonth", False)),
        )
        result = engine.calculate(chart_input)
        chart = result.to_dict()
        bazi_profile = favored_wuxing_from_chart(chart)

    return {
        "fullName": full_name,
        "shuowen": shuowen,
        "charWuxing": char_wuxing,
        "wuge": wuge,
        "baziProfile": bazi_profile,
        "chart": chart,
    }
