from __future__ import annotations

LIU_SHEN_ORDER = ("青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武")

DAY_GAN_START = {
    "甲": 0,
    "乙": 0,
    "丙": 1,
    "丁": 1,
    "戊": 2,
    "己": 3,
    "庚": 4,
    "辛": 4,
    "壬": 5,
    "癸": 5,
}


def liushen_for_day(day_gan: str) -> list[str]:
    start = DAY_GAN_START.get(day_gan, 0)
    return [LIU_SHEN_ORDER[(start + idx) % 6] for idx in range(6)]
