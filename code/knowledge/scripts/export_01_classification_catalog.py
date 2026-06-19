"""Export a human-readable classification catalog for 01八字命理 files."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
ROOT = KNOWLEDGE_DIR.parents[1]
MANIFEST_PATH = KNOWLEDGE_DIR / "data" / "sources" / "bazi_sources_manifest.json"
CSV_OUTPUT = KNOWLEDGE_DIR / "data" / "sources" / "bazi_sources_catalog.csv"
DATABASE_MD_OUTPUT = ROOT / "数据库" / "01八字命理" / "_文件分类清单.md"
REPORT_MD_OUTPUT = ROOT / "report" / "八字判盘最强方案" / "01八字命理文件分类清单.md"

AUTHORITY_LABELS = {
    "S": "S 主裁经典",
    "A": "A 辅助经典",
    "B": "B 现代解释",
    "C": "C 命例经验",
    "D": "D 低信/排除",
}

ROLE_LABELS = {
    "judge_library": "裁判库",
    "experience_library": "经验库",
    "supplement_library": "补充/低信库",
}


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _bool_label(value: object) -> str:
    return "是" if bool(value) else "否"


def _csv_rows(files: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for row in files:
        rows.append(
            {
                "sourceFile": row.get("sourceFile", ""),
                "classic": row.get("classic", ""),
                "legacyTier": row.get("legacyTier", ""),
                "authorityTier": row.get("authorityTier", ""),
                "authorityLabel": AUTHORITY_LABELS.get(row.get("authorityTier", ""), ""),
                "libraryRole": row.get("libraryRole", ""),
                "libraryLabel": ROLE_LABELS.get(row.get("libraryRole", ""), ""),
                "evidenceRole": row.get("evidenceRole", ""),
                "sourceType": row.get("sourceType", ""),
                "canJudge": _bool_label(row.get("canJudge")),
                "canOverride": _bool_label(row.get("canOverride")),
                "canEnterProductionRag": _bool_label(row.get("canEnterProductionRag")),
                "judgmentPolicy": row.get("judgmentPolicy", ""),
                "domains": ",".join(row.get("domains") or []),
            }
        )
    return rows


def _write_csv(rows: list[dict]) -> None:
    CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _table_row(row: dict) -> str:
    return (
        f"| `{row.get('sourceFile', '')}` | {row.get('classic', '')} | "
        f"{row.get('legacyTier', '')} | {row.get('libraryRole', '')} | "
        f"{row.get('evidenceRole', '')} | {_bool_label(row.get('canJudge'))} | "
        f"{row.get('judgmentPolicy', '')} |"
    )


def _build_markdown(payload: dict) -> str:
    files = sorted(
        payload.get("files") or [],
        key=lambda item: (
            str(item.get("authorityTier", "")),
            str(item.get("libraryRole", "")),
            str(item.get("sourceFile", "")),
        ),
    )
    lines: list[str] = [
        "# 01八字命理文件分类清单",
        "",
        f"- 生成时间: {datetime.now().isoformat(timespec='seconds')}",
        f"- manifest 时间: {payload.get('builtAt', '')}",
        f"- 文件总数: {payload.get('filesTotal', 0)}",
        "",
        "## 分类总览",
        "",
        "| 分类 | 数量 | 说明 |",
        "|------|------|------|",
    ]
    by_authority = payload.get("byAuthorityTier") or {}
    for tier in ("S", "A", "B", "C", "D"):
        lines.append(
            f"| {tier} | {by_authority.get(tier, 0)} | {AUTHORITY_LABELS.get(tier, '')} |"
        )
    lines.extend(
        [
            "",
            "## 三库总览",
            "",
            "| 库 | 数量 | 说明 |",
            "|----|------|------|",
        ]
    )
    by_library = payload.get("byLibraryRole") or {}
    for role in ("judge_library", "experience_library", "supplement_library"):
        lines.append(f"| {role} | {by_library.get(role, 0)} | {ROLE_LABELS.get(role, '')} |")

    lines.extend(
        [
            "",
            "## 查看规则",
            "",
            "- `S/A/B` 属于裁判库, 但只有 `canJudge=是` 的文件能进入判盘裁判.",
            "- `C` 是命例经验库, 只能作为 `case_reference`, 不允许主裁.",
            "- `D` 是低信或排除材料, 不进入主裁判断.",
            "- 如果文件名含经典书名但同时是命例或详批, 以命例优先, 分类为 `C`.",
            "",
        ]
    )

    for tier in ("S", "A", "B", "C", "D"):
        grouped = [row for row in files if row.get("authorityTier") == tier]
        lines.extend(
            [
                f"## {tier} - {AUTHORITY_LABELS.get(tier, '')} ({len(grouped)})",
                "",
                "| 文件 | 识别经典/来源 | legacyTier | libraryRole | evidenceRole | canJudge | policy |",
                "|------|----------------|------------|-------------|--------------|----------|--------|",
            ]
        )
        for row in grouped:
            lines.append(_table_row(row))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    payload = _load_manifest()
    rows = _csv_rows(payload.get("files") or [])
    if not rows:
        raise RuntimeError("manifest has no files")
    _write_csv(rows)
    markdown = _build_markdown(payload)
    DATABASE_MD_OUTPUT.write_text(markdown, encoding="utf-8")
    REPORT_MD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD_OUTPUT.write_text(markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "filesTotal": payload.get("filesTotal", 0),
                "byAuthorityTier": payload.get("byAuthorityTier", {}),
                "byLibraryRole": payload.get("byLibraryRole", {}),
                "databaseMarkdown": str(DATABASE_MD_OUTPUT),
                "reportMarkdown": str(REPORT_MD_OUTPUT),
                "csv": str(CSV_OUTPUT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
