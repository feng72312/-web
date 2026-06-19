"""Extract structured case records from C-tier experience library files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
RAG_DIR = ROOT / "code" / "rag"
MANIFEST_PATH = KNOWLEDGE_DIR / "data" / "sources" / "bazi_sources_manifest.json"
OUTPUT = KNOWLEDGE_DIR / "data" / "cases" / "cases.jsonl"
DATA_DIR = ROOT / "数据库" / "01八字命理"

if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))

from doc_reader import read_doc_batch, read_document  # noqa: E402

GANS = list("甲乙丙丁戊己庚辛壬癸")
ZHIS = list("子丑寅卯辰巳午未申酉戌亥")
GANZHI_RE = re.compile(r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])")
EVENT_TAGS = {
    "婚": "marriage",
    "嫁": "marriage",
    "财": "wealth",
    "官": "career",
    "职": "career",
    "病": "health",
    "疾": "health",
    "灾": "disaster",
    "祸": "disaster",
    "丧": "bereavement",
    "子": "children",
    "女": "children",
    "父": "family",
    "母": "family",
    "家": "family",
    "学": "education",
    "考": "education",
    "运": "luck_change",
    "车祸": "disaster",
    "糖尿病": "health",
    "高血压": "health",
    "牢狱": "disaster",
}
CHART_PATTERN_KEYWORDS = (
    "从财格",
    "从杀格",
    "从儿格",
    "化气格",
    "正官格",
    "七杀格",
    "食神格",
    "伤官格",
    "偏财格",
    "正财格",
    "偏印格",
    "正印格",
    "建禄格",
    "阳刃格",
)


def _structure_tags(text: str, ganzhi_list: list[str]) -> list[str]:
    tags: list[str] = []
    if ganzhi_list:
        tags.append(f"pillars:{''.join(ganzhi_list[:4])}")
    for gan in GANS:
        if text.count(gan) >= 4:
            tags.append(f"gan_bias:{gan}")
    for zhi in ZHIS:
        if text.count(zhi) >= 3:
            tags.append(f"zhi_bias:{zhi}")
    return tags[:8]


def _event_tags(text: str, filename: str) -> list[str]:
    tags: list[str] = []
    merged = f"{filename}\n{text}"
    for key, value in EVENT_TAGS.items():
        if key in merged and value not in tags:
            tags.append(value)
    return tags[:6]


def _observed_event(filename: str, text: str) -> str:
    stem = Path(filename).stem
    for token in ("实战命例", "函测命例", "命例"):
        if token in stem:
            stem = stem.split(token, 1)[-1]
    stem = stem.strip("._- ")
    if stem:
        return stem[:80]
    cleaned = re.sub(r"\s+", " ", text[:120]).strip()
    return cleaned[:80]


def _chart_pattern(text: str) -> str:
    for keyword in CHART_PATTERN_KEYWORDS:
        if keyword in text:
            return keyword
    return ""


def _event_years(text: str) -> list[int]:
    years: list[int] = []
    for match in re.finditer(r"(19\d{2}|20\d{2})", text):
        year = int(match.group(1))
        if 1900 <= year <= 2099 and year not in years:
            years.append(year)
    return years[:12]


def _luck_triggers(text: str) -> list[str]:
    triggers: list[str] = []
    for match in re.finditer(
        r"(?:大运|行运|岁运)[^\n。]{0,24}([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])",
        text,
    ):
        gz = match.group(1)
        if gz not in triggers:
            triggers.append(gz)
    for gz in GANZHI_RE.findall(text):
        if len(triggers) >= 6:
            break
        if gz not in triggers:
            triggers.append(gz)
    return triggers[:6]


def _is_readable_text(text: str) -> bool:
    sample = text[:500]
    if not sample.strip():
        return False
    if "PK\x03\x04" in sample or "\u0011\u001a" in sample:
        return False
    ctrl = sum(1 for ch in sample if ord(ch) < 32 and ch not in "\n\r\t")
    if ctrl > max(len(sample) * 0.05, 3):
        return False
    printable = sum(1 for ch in sample if ch.isprintable() or ch in "\n\r\t")
    return printable / max(len(sample), 1) >= 0.7


def _read_case_text(path: Path) -> tuple[str, str | None]:
    try:
        text = read_document(path)
    except Exception as exc:
        return "", f"read_failed:{exc.__class__.__name__}"
    if not _is_readable_text(text):
        return text, "binary_or_unreadable"
    if len(text.strip()) < 80:
        return text, "text_too_short"
    return text, None


def extract_cases(manifest_path: Path) -> list[dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = [
        row
        for row in manifest.get("files", [])
        if row.get("authorityTier") == "C" and row.get("libraryRole") == "experience_library"
    ]
    doc_paths: list[Path] = []
    pending: list[tuple[dict, Path]] = []
    for row in rows:
        source_file = row["sourceFile"]
        path = DATA_DIR / source_file
        if not path.exists():
            continue
        if path.suffix.lower() == ".doc":
            doc_paths.append(path)
        pending.append((row, path))

    doc_texts: dict[Path, str] = {}
    if doc_paths:
        print(f"[cases] reading {len(doc_paths)} doc files via Word batch ...", flush=True)
        try:
            doc_texts = read_doc_batch(doc_paths, batch_size=6)
        except Exception as exc:
            print(f"[cases] doc batch failed: {exc}", flush=True)

    cases: list[dict] = []
    for row, path in pending:
        source_file = row["sourceFile"]
        suffix = path.suffix.lower()
        text = ""
        read_reason: str | None = None
        if suffix == ".doc":
            text = doc_texts.get(path, "")
            if not text:
                read_reason = "read_failed:doc_batch"
            elif not _is_readable_text(text):
                read_reason = "binary_or_unreadable"
            elif len(text.strip()) < 80:
                read_reason = "text_too_short"
        else:
            text, read_reason = _read_case_text(path)
        ganzhi = GANZHI_RE.findall(text) if text else []
        event_tags = _event_tags(text, source_file)
        structure_tags = _structure_tags(text, ganzhi) if text else []
        if read_reason and not event_tags:
            event_tags = _event_tags("", source_file)
        case_id = f"case:{source_file}"
        record = {
            "id": case_id,
            "sourceCategory": "01八字命理",
            "sourceFile": source_file,
            "classic": row.get("classic", source_file),
            "authorityTier": "C",
            "libraryRole": "experience_library",
            "canJudge": False,
            "forbiddenApply": True,
            "structureTags": structure_tags,
            "eventTags": event_tags,
            "eventYear": _event_years(text) if text else [],
            "observedEvent": _observed_event(source_file, text),
            "chartPattern": _chart_pattern(text) if text else "",
            "luckTrigger": _luck_triggers(text) if text else [],
            "verdict": text[:400].replace("\n", " ") if text else "",
            "confidence": "medium" if text and structure_tags else "low",
            "extractedAt": datetime.now().isoformat(timespec="seconds"),
        }
        if read_reason:
            record["doNotApplyReason"] = read_reason
        elif suffix == ".docx" and text and ("目录" in text[:400] or "ISBN" in text[:400]):
            if "乾造" not in text[:1200] and "坤造" not in text[:1200]:
                record["doNotApplyReason"] = "catalog_or_index"
        cases.append(record)
        print(f"[cases] {source_file} tags={len(structure_tags)} reason={read_reason or 'ok'}", flush=True)
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    parser.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"missing manifest: {manifest_path}")
        return 1
    cases = extract_cases(manifest_path)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in cases:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    applicable = sum(1 for row in cases if not row.get("doNotApplyReason"))
    print(f"extracted {len(cases)} cases ({applicable} applicable) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
