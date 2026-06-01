"""Extract Qimen structured nodes from 奇门法窍 (run from repo root).

Usage:
  py knowledge/scripts/extract_qimen_from_faqiao.py
  py knowledge/scripts/extract_qimen_from_faqiao.py --merge
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT.parent / "数据库" / "04奇门遁甲" / "奇门法窍-清-锡孟樨.txt"
OUTPUT = ROOT / "knowledge" / "data" / "graph" / "qimen_nodes_faqiao.jsonl"
MERGE_TARGET = ROOT / "knowledge" / "data" / "graph" / "qimen_nodes.jsonl"
SOURCE_FILE = "奇门法窍-清-锡孟樨.txt"
CATEGORY = "04奇门遁甲"

DOOR_NAMES = ("休", "生", "伤", "杜", "景", "死", "惊", "开")
STAR_SUFFIX = {
    "蓬": "天蓬",
    "芮": "天芮",
    "冲": "天冲",
    "辅": "天辅",
    "禽": "天禽",
    "心": "天心",
    "柱": "天柱",
    "任": "天任",
    "英": "天英",
}
GOD_LINES = {
    "直符": "值符",
    "白虎": "白虎",
    "九天": "九天",
    "九地": "九地",
    "六合": "六合",
    "太阴": "太阴",
    "元武": "玄武",
    "螣蛇": "螣蛇",
    "朱雀": "朱雀",
    "勾陈": "勾陈",
}


def _clean(text: str) -> str:
    text = text.replace("\u3000", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _node(
    node_id: str,
    topic: str,
    lookup_key: dict,
    summary: str,
    *,
    tier: str = "T1",
) -> dict:
    return {
        "id": node_id,
        "topic": topic,
        "sourceTier": tier,
        "sourceCategory": CATEGORY,
        "sourceFile": SOURCE_FILE,
        "lookupKey": lookup_key,
        "summary": summary[:500],
        "claims": [],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "qimen",
    }


def extract_jieqi_rules(text: str) -> list[dict]:
    nodes = []
    yang = re.search(
        r"阳遁顺行节序歌\s*(.+?)\s*阴遁逆行节序歌",
        text,
        re.DOTALL,
    )
    yin = re.search(r"阴遁逆行节序歌\s*(.+?)\s*六甲旬五不遇时", text, re.DOTALL)
    if yang:
        nodes.append(
            _node(
                "ju:yang_dun_ge",
                "ju",
                {"rule": "yang_dun_ge"},
                _clean(yang.group(1)),
            )
        )
    if yin:
        nodes.append(
            _node(
                "ju:yin_dun_ge",
                "ju",
                {"rule": "yin_dun_ge"},
                _clean(yin.group(1)),
            )
        )
    nodes.append(
        _node(
            "ju:maoshan_rule",
            "ju",
            {"method": "maoshan"},
            "茅山道人法: 节气交节即用该节上元, 前60时辰为上元, 次60为中元, 其后为下元, 转盘排天盘八门九星八神.",
        )
    )
    return nodes


def _section_bounds(text: str, title: str, end_title: str) -> tuple[int, int] | None:
    starts = [m.start() for m in re.finditer(re.escape(title), text)]
    if not starts:
        return None
    start = starts[-1]
    end = text.find(end_title, start + len(title))
    if end < 0 or end - start < 200:
        return None
    return start, end


def extract_men_xing(text: str) -> list[dict]:
    bounds = _section_bounds(text, "八门九星吉凶克应", "八门临时断绝")
    if not bounds:
        return []
    start, end = bounds
    section = text[start:end]
    lines = [_clean(line) for line in section.splitlines() if line.strip()]
    nodes: list[dict] = []
    door_buf: list[str] = []
    star_buf: list[str] = []

    def flush_pair() -> None:
        nonlocal door_buf, star_buf
        if door_buf:
            door_text = " ".join(door_buf)
            m = re.match(r"^([\u4e00-\u9fff]门)为", door_text)
            if m:
                door_label = m.group(1)
                nodes.append(
                    _node(
                        f"men:{door_label}",
                        "men",
                        {"door": door_label},
                        door_text,
                    )
                )
        if star_buf:
            star_text = " ".join(star_buf)
            m = re.match(r"^天(\S星)", star_text)
            if m:
                short = m.group(1).replace("星", "")
                star_label = STAR_SUFFIX.get(short, f"天{short}")
                nodes.append(
                    _node(
                        f"xing:{star_label}",
                        "xing",
                        {"star": star_label},
                        star_text,
                    )
                )
        door_buf = []
        star_buf = []

    for line in lines:
        line = re.sub(r"^[　\s]+", "", line)
        if "八门九星" in line and "克应" in line:
            continue
        if re.match(r"^[\u4e00-\u9fff]门为", line):
            flush_pair()
            door_buf = [line]
            continue
        if re.match(r"^天[\u4e00-\u9fff]+星", line):
            if door_buf:
                star_buf = [line]
            continue
        if door_buf and not star_buf:
            door_buf.append(line)
        elif star_buf:
            star_buf.append(line)
    flush_pair()
    return nodes


def extract_shen(text: str) -> list[dict]:
    starts = [m.start() for m in re.finditer("八诈八属", text)]
    if not starts:
        return []
    start = starts[-1]
    end = text.find("论干支合变", start)
    section = text[start : end if end > 0 else start + 800]
    nodes: list[dict] = []
    for key, label in GOD_LINES.items():
        pat = rf"{key}[^。\n]*属[金木水火土]"
        m = re.search(pat, section)
        if m:
            nodes.append(
                _node(
                    f"shen:{label}",
                    "shen",
                    {"god": label},
                    _clean(m.group(0)),
                    tier="T2",
                )
            )
    block = re.search(
        r"八诈之中[^。]+。",
        text,
    )
    if block:
        nodes.append(
            _node(
                "shen:bazha_rule",
                "shen",
                {"rule": "bazha"},
                _clean(block.group(0)),
            )
        )
    return nodes


def extract_yong(text: str) -> list[dict]:
    nodes = [
        _node(
            "yong:shizhan_faqiao",
            "yong",
            {"category": "shizhan"},
            "事占: 先看值符值使与门星神生克, 再结合方位与三奇吉凶格, 法窍卷四论主客应期.",
            tier="T2",
        ),
        _node(
            "yong:xingzhan_faqiao",
            "yong",
            {"category": "xingzhan"},
            "行占: 重开门休生三吉门与驿马方向, 茅山顺节三元, 远行忌旬空入墓.",
            tier="T2",
        ),
    ]
    return nodes


def _read_source(source: Path) -> str:
    for enc in ("utf-8", "gb18030", "gbk"):
        try:
            return source.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return source.read_text(encoding="utf-8", errors="ignore")


def extract_all(source: Path) -> list[dict]:
    text = _read_source(source)
    nodes: list[dict] = []
    nodes.extend(extract_jieqi_rules(text))
    nodes.extend(extract_men_xing(text))
    nodes.extend(extract_shen(text))
    nodes.extend(extract_yong(text))
    seen: set[str] = set()
    unique: list[dict] = []
    for n in nodes:
        if n["id"] in seen:
            continue
        seen.add(n["id"])
        unique.append(n)
    return unique


def merge_into(target: Path, extracted: list[dict]) -> None:
    existing: dict[str, dict] = {}
    if target.exists():
        for line in target.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            existing[row["id"]] = row
    for row in extracted:
        existing[row["id"]] = row
    target.write_text(
        "\n".join(json.dumps(v, ensure_ascii=False) for v in existing.values())
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument(
        "--merge",
        action="store_true",
        help="merge into qimen_nodes.jsonl (overwrites same id)",
    )
    args = parser.parse_args()
    if not args.source.exists():
        raise SystemExit(f"source not found: {args.source}")
    nodes = extract_all(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(n, ensure_ascii=False) for n in nodes) + "\n",
        encoding="utf-8",
    )
    print(f"extracted {len(nodes)} nodes -> {args.output}")
    if args.merge:
        merge_into(MERGE_TARGET, nodes)
        print(f"merged into {MERGE_TARGET}")


if __name__ == "__main__":
    main()
