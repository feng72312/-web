# -*- coding: utf-8 -*-
"""Fetch Bazi classic texts from public online sources into local txt files."""

from __future__ import annotations

import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

OUT_DIR = Path(r"d:\ZY\数据库\八字\1")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BaziClassicFetcher/1.0",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
REQUEST_DELAY = 1.5

CTEXT_BOOKS = [
    {
        "filename": "01_滴天髓阐微_任铁樵注.txt",
        "title": "滴天髓阐微 (任铁樵增注, 含原文与详解)",
        "url": "https://ctext.org/wiki.pl?chapter=126492&if=gb&remap=gb",
        "source": "中国哲学书电子化计划 (ctext.org)",
    },
    {
        "filename": "02_子平真诠评注_沈孝瞻原著.txt",
        "title": "子平真诠评注 (沈孝瞻原著, 含评注)",
        "url": "https://ctext.org/wiki.pl?chapter=974137&if=gb&remap=gb",
        "source": "中国哲学书电子化计划 (ctext.org)",
    },
    {
        "filename": "03_渊海子平_徐大升.txt",
        "title": "渊海子平 (徐大升编著)",
        "url": "https://ctext.org/wiki.pl?chapter=524726&if=gb&remap=gb",
        "source": "中国哲学书电子化计划 (ctext.org)",
    },
    {
        "filename": "04_穷通宝鉴_余春台.txt",
        "title": "穷通宝鉴 (余春台整理)",
        "url": "https://ctext.org/wiki.pl?chapter=208379&if=gb&remap=gb",
        "source": "中国哲学书电子化计划 (ctext.org)",
    },
    {
        "filename": "05_千里命稿_韦千里.txt",
        "title": "千里命稿 (韦千里著, 含讲义与评断)",
        "url": "https://ctext.org/wiki.pl?chapter=933376&if=gb&remap=gb",
        "source": "中国哲学书电子化计划 (ctext.org)",
    },
]

QIONGTONG_YILIAI = {
    "filename": "04b_穷通宝鉴_白话详解_yiliai.txt",
    "title": "穷通宝鉴 (含白话注解, YiLiAi 站点)",
    "base_url": "https://www.yiliai.com.cn/press/know/books/qtbj/",
    "chapters": [
        ("01.html", "五行总论"),
        ("02.html", "甲木总论"),
        ("03.html", "乙木总论"),
        ("04.html", "丙火总论"),
        ("05.html", "丁火总论"),
        ("06.html", "戊土总论"),
        ("07.html", "己土总论"),
        ("08.html", "庚金总论"),
        ("09.html", "辛金总论"),
        ("10.html", "壬水总论"),
        ("11.html", "癸水总论"),
    ],
    "source": "YiLiAi (www.yiliai.com.cn)",
}


def fetch_url(url: str, timeout: int = 120) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def parse_ctext_wiki(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    lines: list[str] = []

    title_el = soup.find("h2")
    if title_el:
        lines.append(title_el.get_text(strip=True))
        lines.append("=" * 40)
        lines.append("")

    tables = soup.find_all("table")
    table = max(tables, key=lambda t: len(t.find_all("tr")), default=None) if tables else None
    if not table or len(table.find_all("tr")) < 5:
        main = soup.find("div", id="content") or soup.body
        text = main.get_text("\n", strip=True) if main else soup.get_text("\n", strip=True)
        return re.sub(r"\n{3,}", "\n\n", text)

    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        parts = [c.get_text(" ", strip=True) for c in cells if c.get_text(strip=True)]
        if not parts:
            continue
        if len(parts) == 1:
            lines.append(parts[0])
        else:
            num = parts[0]
            body = " ".join(parts[1:])
            if num.isdigit():
                lines.append(f"\n[{num}] {body}")
            else:
                lines.append(" | ".join(parts))
        lines.append("")

    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def parse_yiliai_chapter(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("article") or soup.find("main") or soup.body
    if not main:
        return soup.get_text("\n", strip=True)

    for tag in main.find_all(["script", "style", "nav", "footer"]):
        tag.decompose()

    lines: list[str] = []
    for el in main.find_all(["h1", "h2", "h3", "p", "li"]):
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        if el.name.startswith("h"):
            lines.append("")
            lines.append(text)
            lines.append("-" * min(len(text), 30))
        else:
            lines.append(text)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def write_book(path: Path, header: str, body: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"{header}\n\n{'=' * 50}\n\n{body}\n"
    path.write_text(content, encoding="utf-8")
    return len(body)


def fetch_ctext_books() -> list[dict]:
    results = []
    for book in CTEXT_BOOKS:
        out_path = OUT_DIR / book["filename"]
        print(f"Fetching: {book['title']}")
        try:
            html = fetch_url(book["url"])
            body = parse_ctext_wiki(html)
            header = (
                f"书名: {book['title']}\n"
                f"来源: {book['source']}\n"
                f"URL: {book['url']}\n"
                f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            chars = write_book(out_path, header, body)
            results.append({"file": book["filename"], "status": "ok", "chars": chars})
            print(f"  -> saved {out_path.name} ({chars} chars)")
        except Exception as exc:
            results.append({"file": book["filename"], "status": f"error: {exc}"})
            print(f"  -> FAILED: {exc}")
        time.sleep(REQUEST_DELAY)
    return results


def fetch_qiongtong_yiliai() -> dict:
    cfg = QIONGTONG_YILIAI
    out_path = OUT_DIR / cfg["filename"]
    print(f"Fetching: {cfg['title']}")
    parts: list[str] = []
    for page, name in cfg["chapters"]:
        url = urljoin(cfg["base_url"], page)
        print(f"  chapter: {name}")
        try:
            html = fetch_url(url)
            text = parse_yiliai_chapter(html)
            parts.append(f"\n\n{'#' * 20}\n# {name}\n{'#' * 20}\n\n{text}")
        except Exception as exc:
            parts.append(f"\n\n# {name}\n[抓取失败: {exc}]")
        time.sleep(REQUEST_DELAY)

    body = "\n".join(parts).strip()
    header = (
        f"书名: {cfg['title']}\n"
        f"来源: {cfg['source']}\n"
        f"URL: {cfg['base_url']}\n"
        f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    chars = write_book(out_path, header, body)
    print(f"  -> saved {out_path.name} ({chars} chars)")
    return {"file": cfg["filename"], "status": "ok", "chars": chars}


def write_index(results: list[dict]) -> None:
    index_path = OUT_DIR / "00_资料来源索引.txt"
    lines = [
        "八字命理典籍 - 网络公开资料索引",
        "=" * 50,
        f"整理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"存放目录: {OUT_DIR}",
        "",
        "一、已下载本地文件",
        "",
    ]
    for r in results:
        status = r.get("status", "unknown")
        chars = r.get("chars", 0)
        line = f"- {r['file']}: {status}"
        if chars:
            line += f" ({chars} 字)"
        lines.append(line)

    lines.extend(
        [
            "",
            "二、各书在线来源 (可进一步查阅)",
            "",
            "1. 滴天髓阐微 (任铁樵注)",
            "   https://ctext.org/wiki.pl?chapter=126492&if=gb",
            "   https://www.muxiangge.com/guji/ditiansuichanwei",
            "",
            "2. 子平真诠评注 (沈孝瞻原著, 徐乐吾评注版见国学资源网)",
            "   https://ctext.org/wiki.pl?chapter=974137&if=gb",
            "   https://www.suanzhun.net/dianji/zipingzhen/",
            "",
            "3. 渊海子平 (徐大升)",
            "   https://ctext.org/wiki.pl?chapter=524726&if=gb",
            "   https://zh.wikisource.org/wiki/渊海子平",
            "   https://www.8bei8.com/book/yuanhaiziping.html",
            "",
            "4. 穷通宝鉴 (余春台整理, 徐乐吾评注)",
            "   https://ctext.org/wiki.pl?chapter=208379&if=gb",
            "   https://www.yiliai.com.cn/press/know/books/qtbj/",
            "   https://www.8bei8.com/book/qiongtongbaojian.html",
            "",
            "5. 千里命稿 (韦千里)",
            "   https://ctext.org/wiki.pl?chapter=933376&if=gb",
            "   https://gujifu.cn/wen/130.html",
            "",
            "三、说明",
            "",
            "- 以上资料均来自公开网络, 仅供个人学习研究",
            "- ctext.org 为学术性公开文本库, 内容以繁体/简体混排为主",
            "- 穷通宝鉴白话详解来自 YiLiAi 站点, 与 ctext 原文互为补充",
            "- 如需徐乐吾评注版 PDF, 可在国学资源网检索下载",
            "- 上级目录已有部分 PDF/EPUB 扫描版, 可与本文本对照",
        ]
    )
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Index saved: {index_path.name}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = fetch_ctext_books()
    results.append(fetch_qiongtong_yiliai())
    write_index(results)
    ok = sum(1 for r in results if r.get("status") == "ok")
    print(f"\nDone: {ok}/{len(results)} files saved to {OUT_DIR}")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
