from __future__ import annotations

from typing import Any

LIUREN_TOPICS = ("yue_jiang", "ge_ju", "tian_jiang", "si_ke", "san_chuan", "shen_sha", "jinkou", "yong")


def build_liuren_lookup_keys(chart: dict[str, Any]) -> dict[str, dict[str, str]]:
    keys: dict[str, dict[str, str]] = {}
    inp = chart.get("input") or {}
    lr = chart.get("liuren") or {}
    if lr:
        keys["yue_jiang"] = {"yueJiang": lr.get("yueJiang", "")}
        ge = lr.get("geJu") or {}
        keys["ge_ju"] = {"name": ge.get("name", ""), "sub": ge.get("sub", "")}
        chu = (lr.get("sanChuan") or {}).get("chu") or {}
        if chu.get("general"):
            keys["tian_jiang"] = {"general": chu.get("general", "")}
        keys["si_ke"] = {"pattern": "四课"}
        sc = lr.get("sanChuan") or {}
        if sc.get("chu"):
            keys["san_chuan"] = {"role": "初传"}
        elif sc.get("zhong"):
            keys["san_chuan"] = {"role": "中传"}
        elif sc.get("mo"):
            keys["san_chuan"] = {"role": "末传"}
        sha = lr.get("shenSha") or {}
        if sha:
            first = next(iter(sha.keys()), "")
            if first:
                keys["shen_sha"] = {"name": first}
    jk = chart.get("jinkou") or {}
    if jk:
        keys["jinkou"] = {"renYuan": jk.get("renYuan", ""), "difen": jk.get("difen", "")}
    keys["yong"] = {"category": inp.get("category", "shizhan")}
    return keys
