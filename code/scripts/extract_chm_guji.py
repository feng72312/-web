# -*- coding: utf-8 -*-
"""Extract CHM decompiled HTML books into classified txt under 未入库古籍/1."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
CHM_DIR = ROOT / "未入库古籍"
OUTPUT_DIR = CHM_DIR / "1"

# (decompile_subdir, default_category, chm_keyword for matching source file)
CHM_SOURCES = (
    ("_tmp_chm_liuren", "05大六壬", "六壬"),
    ("_tmp_chm_meihua", "03梅花易学", "梅花"),
)

SKIP_DIRS = {"TP2", "TP4", "images", "Images", "image", "Image"}

# book_name -> category override
CATEGORY_OVERRIDES: dict[str, str] = {
    "测字秘牒": "12实用专区",
    "周公解梦": "12实用专区",
    "诸葛神数": "12实用专区",
    "易医玄经": "10杂占方术",
    "周易参同契": "12周易",
}

# classic Zhou Yi texts (not Mei Hua / Huang Ji specialty)
ZHOUYI_BOOKS = frozenset(
    {
        "东坡易传",
        "周易全解",
        "周易本义",
        "周易江湖",
        "周易注",
        "周易略例",
        "周易白话解",
        "周易集解",
        "子夏易传",
        "新本郑氏周易",
        "易图讲座",
        "易童子问",
        "易经",
        "易经六十四卦注解",
        "易经明道录",
        "易经证释",
        "易经（白话版）",
    }
)

MEIHUA_KEYWORDS = ("梅花", "皇极", "心易", "观梅", "拆字", "刀骨")

AUTHOR_PATTERNS = (
    re.compile(r"([唐宋元明清民国汉魏晋南北朝辽金][\u4e00-\u9fff·\s]{0,8}[·\s][\u4e00-\u9fff]{1,8})撰"),
    re.compile(r"([唐宋元明清民国][\u4e00-\u9fff·\s]{0,8}[·\s][\u4e00-\u9fff]{1,8})著"),
    re.compile(r"([唐宋元明清民国][\u4e00-\u9fff·\s]{0,8}[·\s][\u4e00-\u9fff]{1,8})编"),
)


def decompile_chm(chm_path: Path, out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    subprocess.run(
        ["C:\\Windows\\hh.exe", "-decompile", str(out_dir), str(chm_path)],
        check=True,
    )


def read_html(path: Path) -> str:
    for enc in ("gb2312", "gbk", "gb18030", "utf-8"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="gbk", errors="replace")


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "meta", "link"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sorted_mydoc_files(book_dir: Path) -> list[Path]:
    files = []
    for path in book_dir.glob("mydoc*.htm*"):
        m = re.search(r"mydoc(\d+)", path.stem, re.I)
        if m:
            files.append((int(m.group(1)), path))
    files.sort(key=lambda x: x[0])
    return [p for _, p in files]


def guess_author(text: str) -> str:
    head = text[:3000]
    for pat in AUTHOR_PATTERNS:
        m = pat.search(head)
        if m:
            return m.group(1).replace(" ", "").strip()
    return "佚名"


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"\s+", "", name)
    return name.strip("._")


def classify_book(book_name: str, default_category: str) -> str:
    if book_name in CATEGORY_OVERRIDES:
        return CATEGORY_OVERRIDES[book_name]
    if any(k in book_name for k in ("测字", "解梦", "梦占")):
        return "12实用专区"
    if any(k in book_name for k in ("诸葛神数", "签诗")):
        return "12实用专区"
    if any(k in book_name for k in ("六壬", "金口", "壬归", "壬占")):
        return "05大六壬"
    if book_name in ZHOUYI_BOOKS:
        return "12周易"
    if any(k in book_name for k in MEIHUA_KEYWORDS):
        return "03梅花易学"
    if any(k in book_name for k in ("周易", "易经")) and not any(
        k in book_name for k in MEIHUA_KEYWORDS
    ):
        return "12周易"
    return default_category


def extract_book(book_dir: Path, default_category: str) -> tuple[str, str, str, str] | None:
    pages = sorted_mydoc_files(book_dir)
    if not pages:
        return None

    parts: list[str] = []
    for page in pages:
        chunk = html_to_text(read_html(page))
        if chunk:
            parts.append(chunk)
    if not parts:
        return None

    book_name = book_dir.name
    category = classify_book(book_name, default_category)
    body = "\n\n".join(parts)
    author = guess_author(body)
    return book_name, category, author, body


def ensure_decompiled() -> None:
    chm_files = list(CHM_DIR.glob("*.chm"))
    mapping = {
        "六壬": CHM_DIR / "_tmp_chm_liuren",
        "梅花": CHM_DIR / "_tmp_chm_meihua",
    }
    for chm in chm_files:
        for key, out_dir in mapping.items():
            if key in chm.name and not out_dir.exists():
                print(f"[decompile] {chm.name} -> {out_dir.name}", flush=True)
                decompile_chm(chm, out_dir)


def run(output_dir: Path = OUTPUT_DIR) -> int:
    ensure_decompiled()
    output_dir.mkdir(parents=True, exist_ok=True)

    stats: list[dict] = []
    for subdir, default_cat, _ in CHM_SOURCES:
        src_root = CHM_DIR / subdir
        if not src_root.exists():
            print(f"[skip] missing {src_root}", flush=True)
            continue

        for book_dir in sorted(src_root.iterdir()):
            if not book_dir.is_dir() or book_dir.name in SKIP_DIRS:
                continue
            result = extract_book(book_dir, default_cat)
            if not result:
                print(f"[empty] {book_dir.name}", flush=True)
                continue

            book_name, category, author, body = result
            cat_dir = output_dir / category
            cat_dir.mkdir(parents=True, exist_ok=True)

            fname = sanitize_filename(f"{book_name}-{author}.txt")
            out_path = cat_dir / fname
            header = f"《{book_name}》\n来源: CHM典藏\n作者: {author}\n分类: {category}\n\n"
            out_path.write_text(header + body, encoding="utf-8")
            stats.append(
                {
                    "book": book_name,
                    "category": category,
                    "file": str(out_path.relative_to(ROOT)),
                    "chars": len(body),
                }
            )
            print(f"[ok] {category}/{fname} ({len(body)} chars)", flush=True)

    index_path = output_dir / "_index.json"
    import json

    index_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nDone: {len(stats)} books -> {output_dir}", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract CHM books to 未入库古籍/1")
    parser.add_argument("--output", default=str(OUTPUT_DIR))
    args = parser.parse_args()
    return run(Path(args.output))


if __name__ == "__main__":
    sys.exit(main())
