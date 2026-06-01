"""Extract Liuren structured nodes from 六壬指南 (run from repo root).

Usage:
  py knowledge/scripts/extract_liuren_from_zhinan.py
  py knowledge/scripts/extract_liuren_from_zhinan.py --merge
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
DEFAULT_SOURCE = ROOT.parent / "数据库" / "05大六壬" / "六壬指南-明-陈公献.txt"
OUTPUT = ROOT / "knowledge" / "data" / "graph" / "liuren_nodes_zhinan.jsonl"
MERGE_TARGET = ROOT / "knowledge" / "data" / "graph" / "liuren_nodes.jsonl"
SOURCE_FILE = "六壬指南-明-陈公献.txt"
CATEGORY = "05大六壬"

GE_JU_KEYWORDS = (
    "贼克",
    "比用",
    "涉害",
    "遥克",
    "昴星",
    "别责",
    "八专",
    "伏吟",
    "反吟",
)
SHEN_SHA_NAMES = (
    "日马",
    "月马",
    "丁马",
    "天马",
    "驿马",
    "华盖",
    "闪电",
    "旬空",
    "贵人",
    "冲",
    "合",
    "刑",
    "害",
    "破",
    "季",
    "墓",
)


def _read_source(source: Path) -> str:
    for enc in ("gb18030", "gbk", "utf-8"):
        try:
            return source.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return source.read_text(encoding="utf-8", errors="ignore")


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
        "summary": summary[:600],
        "claims": [],
        "agreementLevel": "single_source",
        "safeAutoAnswer": False,
        "domain": "liuren",
    }


def _section_bounds(text: str, start_title: str, end_title: str) -> tuple[int, int] | None:
    starts = [m.start() for m in re.finditer(re.escape(start_title), text)]
    if not starts:
        return None
    start = starts[-1]
    end = text.find(end_title, start + len(start_title))
    if end < 0 or end - start < 80:
        return None
    return start, end


def _split_paragraphs(section: str) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if not line or line in ("卷一", "卷二", "卷三", "目录"):
            if buf:
                chunks.append(_clean("".join(buf)))
                buf = []
            continue
        if re.match(r"^卷[一二三四五六七八九十]", line) and len(line) < 8:
            if buf:
                chunks.append(_clean("".join(buf)))
                buf = []
            continue
        buf.append(line)
    if buf:
        chunks.append(_clean("".join(buf)))
    merged: list[str] = []
    for c in chunks:
        if len(c) < 12:
            continue
        if len(c) > 400:
            parts = re.split(r"(?<=[。；])", c)
            for p in parts:
                p = p.strip()
                if len(p) >= 12:
                    merged.append(p)
        else:
            merged.append(c)
    return merged


def _topic_for_paragraph(para: str, default: str) -> str:
    if any(k in para for k in ("四课", "一课", "二课", "三课")):
        return "si_ke"
    if any(k in para for k in ("初传", "中传", "末传", "三传")):
        return "san_chuan"
    if any(k in para for k in GE_JU_KEYWORDS):
        return "ge_ju"
    if any(k in para for k in SHEN_SHA_NAMES):
        return "shen_sha"
    if any(k in para for k in ("贵人", "天将", "螣蛇", "朱雀", "六合", "青龙", "白虎")):
        return "tian_jiang"
    if any(k in para for k in ("月将", "登明", "河魁", "从魁", "传送", "小吉", "胜光")):
        return "yue_jiang"
    if "金口诀" in para or "人元" in para or "地分" in para:
        return "jinkou"
    return default


def _lookup_for_topic(topic: str, para: str, idx: int) -> dict:
    if topic == "ge_ju":
        for name in GE_JU_KEYWORDS:
            if name in para:
                return {"name": name, "sub": ""}
    if topic == "si_ke":
        return {"pattern": "四课"}
    if topic == "san_chuan":
        role = "初传"
        if "中传" in para:
            role = "中传"
        elif "末传" in para:
            role = "末传"
        return {"role": role}
    if topic == "shen_sha":
        for name in SHEN_SHA_NAMES:
            if name in para:
                return {"name": name}
    if topic == "tian_jiang":
        for gen in (
            "贵人",
            "螣蛇",
            "朱雀",
            "六合",
            "勾陈",
            "青龙",
            "天空",
            "白虎",
            "太常",
            "玄武",
            "太阴",
            "天后",
        ):
            if gen in para:
                return {"general": gen}
    if topic == "yue_jiang":
        for zhi, name in (
            ("亥", "登明"),
            ("戌", "河魁"),
            ("酉", "从魁"),
            ("申", "传送"),
            ("未", "小吉"),
            ("午", "胜光"),
            ("巳", "太乙"),
            ("辰", "天罡"),
            ("卯", "太冲"),
            ("寅", "功曹"),
            ("丑", "大吉"),
            ("子", "神后"),
        ):
            if name in para:
                return {"yueJiang": name}
    if topic == "jinkou":
        return {"renYuan": "", "difen": ""}
    return {"ref": f"zhinan_{idx}"}


def extract_xinyin_zhangzhi(text: str) -> list[dict]:
    nodes: list[dict] = []
    xb = _section_bounds(text, "心印赋", "指掌赋")
    if xb:
        section = text[xb[0] : xb[1]]
        for idx, para in enumerate(_split_paragraphs(section)):
            topic = _topic_for_paragraph(para, "yong")
            lid = _lookup_for_topic(topic, para, idx)
            nodes.append(
                _node(
                    f"xinyin:{idx}",
                    topic,
                    lid,
                    para,
                    tier="T1",
                )
            )
    zb = _section_bounds(text, "指掌赋", "卷二")
    if zb is None:
        zb = _section_bounds(text, "指掌赋", "毕法")
    if zb:
        section = text[zb[0] : zb[1]]
        for idx, para in enumerate(_split_paragraphs(section)):
            topic = _topic_for_paragraph(para, "yong")
            lid = _lookup_for_topic(topic, para, 1000 + idx)
            nodes.append(
                _node(
                    f"zhangzhi:{idx}",
                    topic,
                    lid,
                    para,
                    tier="T1",
                )
            )
    return nodes


def collect_geju_nodes() -> list[dict]:
    sys.path.insert(0, str(BACKEND))
    from app.core.liuren.engine import LiurenEngine
    from app.core.liuren.models import LiurenInput

    engine = LiurenEngine()
    seen: set[tuple[str, str]] = set()
    nodes: list[dict] = []
    for year in (2024, 2025, 2026):
        for month in range(1, 13):
            for day in range(1, 29):
                for hour in range(0, 24, 2):
                    try:
                        d = engine.chart(
                            LiurenInput(
                                question="collect",
                                year=year,
                                month=month,
                                day=day,
                                hour=hour,
                            )
                        ).to_dict()
                    except Exception:
                        continue
                    ge = (d.get("liuren") or {}).get("geJu") or {}
                    name = ge.get("name", "")
                    sub = ge.get("sub", "")
                    if not name:
                        continue
                    key = (name, sub)
                    if key in seen:
                        continue
                    seen.add(key)
                    sid = re.sub(r"[^\w\u4e00-\u9fff]+", "_", f"{name}_{sub}")[:48]
                    nodes.append(
                        _node(
                            f"ge_ju:{sid}",
                            "ge_ju",
                            {"name": name, "sub": sub},
                            f"课体 {name} {sub}: 九宗门格局之一, 见指南心印指掌与课传参断.",
                            tier="T2",
                        )
                    )
    return nodes


def extract_shensha_glossary() -> list[dict]:
    gloss = {
        "日马": "驿马, 出行、迁动、信息速达.",
        "月马": "月建所主之马, 主一月内动变.",
        "丁马": "旬丁所主之马, 主迟滞后动.",
        "天马": "与天马同参, 主远行、公差.",
        "华盖": "主孤、盖、学术、宗教、掩藏.",
        "闪电": "主突发、惊恐、电火之事.",
        "旬空": "旬空临传, 事多虚诈或延期.",
        "贵人": "天乙贵人, 主贵人、官长、机遇.",
        "冲": "地支相冲, 主破、动、变、争.",
        "合": "干支相合, 主和合、牵绊、迟滞.",
        "刑": "三刑、自刑, 主刑伤、口舌、官非.",
        "季": "四季旺衰, 主时令强弱.",
        "墓": "入墓, 主隐藏、停滞、库房.",
    }
    return [
        _node(f"shen_sha:{name}", "shen_sha", {"name": name}, text, tier="T2")
        for name, text in gloss.items()
    ]


def extract_si_ke_san_chuan_rules() -> list[dict]:
    return [
        _node(
            "si_ke:rule",
            "si_ke",
            {"pattern": "四课"},
            "四课: 一课上克下、二课下贼上、三课比用、四课涉害, 为九宗门取初传之基.",
        ),
        _node(
            "san_chuan:chu",
            "san_chuan",
            {"role": "初传"},
            "初传: 发用之始, 断事之发端与起因, 乘天将定吉凶倾向.",
        ),
        _node(
            "san_chuan:zhong",
            "san_chuan",
            {"role": "中传"},
            "中传: 事之中段, 发展过程与转折.",
        ),
        _node(
            "san_chuan:mo",
            "san_chuan",
            {"role": "末传"},
            "末传: 事之结局、归宿与应期.",
        ),
    ]


def extract_all(source: Path, *, with_geju: bool = True) -> list[dict]:
    text = _read_source(source)
    nodes: list[dict] = []
    nodes.extend(extract_xinyin_zhangzhi(text))
    nodes.extend(extract_si_ke_san_chuan_rules())
    nodes.extend(extract_shensha_glossary())
    if with_geju:
        nodes.extend(collect_geju_nodes())
    seen: set[str] = set()
    out: list[dict] = []
    for n in nodes:
        if n["id"] in seen:
            continue
        seen.add(n["id"])
        out.append(n)
    return out


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
    parser.add_argument("--no-geju", action="store_true", help="skip geju collection")
    parser.add_argument(
        "--merge",
        action="store_true",
        help="merge into liuren_nodes.jsonl",
    )
    args = parser.parse_args()
    if not args.source.exists():
        raise SystemExit(f"source not found: {args.source}")
    nodes = extract_all(args.source, with_geju=not args.no_geju)
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
