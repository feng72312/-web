from __future__ import annotations

import random
from datetime import datetime

from app.core.liuyao.calendar_ctx import resolve_calendar_context
from app.core.liuyao.models import LiuyaoInput
from app.core.liuyao.trigrams import mod6, mod8, trigram_id, trigram_to_yao_values, TRIGRAM_IDS


def coin_tails_to_value(tails: int) -> int:
    """tails = number of coin backs (背). 3 backs old yang, 0 backs old yin."""
    if tails == 3:
        return 9
    if tails == 0:
        return 6
    if tails == 2:
        return 8
    return 7


def random_coin_line() -> int:
    tails = sum(1 for _ in range(3) if random.randint(0, 1) == 1)
    return coin_tails_to_value(tails)


def lines_from_trigrams(upper_id: int, lower_id: int, moving: int) -> list[int]:
    lower_vals = trigram_to_yao_values(TRIGRAM_IDS[lower_id])
    upper_vals = trigram_to_yao_values(TRIGRAM_IDS[upper_id])
    lines = lower_vals + upper_vals
    moving_idx = moving - 1
    if lines[moving_idx] == 7:
        lines[moving_idx] = 9
    else:
        lines[moving_idx] = 6
    return lines


def lines_from_meihua_numbers(upper_id: int, lower_id: int, moving: int) -> list[int]:
    return lines_from_trigrams(upper_id, lower_id, moving)


def cast_from_coin(coin_lines: list[int] | None) -> tuple[list[int], str]:
    if coin_lines is None:
        raise ValueError("coinLines required for coin method")
    if len(coin_lines) != 6:
        raise ValueError("coinLines must contain 6 values")
    for value in coin_lines:
        if value not in (6, 7, 8, 9):
            raise ValueError("invalid coin line value")
    return coin_lines, "三钱摇卦六次"


def cast_from_numbers(numbers: list[int] | None) -> tuple[list[int], str]:
    if not numbers:
        raise ValueError("numbers required for number method")
    if len(numbers) not in (1, 2, 3):
        raise ValueError("numbers length must be 1, 2, or 3")
    for num in numbers:
        if num <= 0:
            raise ValueError("numbers must be positive integers")

    if len(numbers) == 1:
        num = numbers[0]
        upper = mod8(num)
        lower = mod8(num // 8)
        moving = mod6(sum(int(ch) for ch in str(abs(num))))
        note = f"梅花单数起卦: {num}"
    elif len(numbers) == 2:
        upper = mod8(numbers[0])
        lower = mod8(numbers[1])
        moving = mod6(numbers[0] + numbers[1])
        note = f"梅花双数起卦: {numbers[0]}, {numbers[1]}"
    else:
        upper = mod8(numbers[0])
        lower = mod8(numbers[1])
        moving = mod6(numbers[2])
        note = f"梅花三数起卦: {numbers[0]}, {numbers[1]}, {numbers[2]}"

    lines = lines_from_meihua_numbers(upper, lower, moving)
    return lines, note


def cast_from_time(data: LiuyaoInput) -> tuple[list[int], str]:
    ctx = resolve_calendar_context(data)
    upper = mod8(ctx["upper_num"])
    lower = mod8(ctx["lower_num"])
    moving = mod6(ctx["moving_num"])
    lines = lines_from_meihua_numbers(upper, lower, moving)
    note = (
        f"农历时间起卦: 年支{ctx['year_zhi_num']} "
        f"月{ctx['lunar_month']} 日{ctx['lunar_day']} 时支{ctx['hour_zhi_num']}"
    )
    return lines, note


def cast_lines(data: LiuyaoInput) -> tuple[list[int], str]:
    if data.method == "coin":
        return cast_from_coin(data.coin_lines)
    if data.method == "number":
        return cast_from_numbers(data.numbers)
    if data.method == "time":
        return cast_from_time(data)
    raise ValueError(f"unsupported method: {data.method}")
