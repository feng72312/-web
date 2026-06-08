# -*- coding: utf-8 -*-
"""Fetch naming-related classic texts into local txt files."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT_DIR = Path(r"d:\ZY\数据库\12实用专区\起名")
SHUOWEN_DATA = Path(r"d:\ZY\_tmp_shuowen\data")
SHUOWEN_REPO = "https://github.com/shuowenjiezi/shuowen.git"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) QimingBookFetcher/1.0",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
REQUEST_DELAY = 2.0
MAX_RETRIES = 3

SHIMING_CHAPTERS = [
    ("释天", "shi-ming/shi-tian/zhs"),
    ("释地", "shi-ming/shi-di/zhs"),
    ("释山", "shi-ming/shi-shan/zhs"),
    ("释水", "shi-ming/shi-shui/zhs"),
    ("释丘", "shi-ming/shi-qiu/zhs"),
    ("释道", "shi-ming/shi-dao/zhs"),
    ("释州国", "shi-ming/shi-zhou-guo/zhs"),
    ("释形体", "shi-ming/shi-xing-ti/zhs"),
    ("释姿容", "shi-ming/shi-zi-rong/zhs"),
    ("释长幼", "shi-ming/shi-chang-you/zhs"),
    ("释亲属", "shi-ming/shi-qin-shu/zhs"),
    ("释言语", "shi-ming/shi-yan-yu/zhs"),
    ("释饮食", "shi-ming/shi-yin-shi/zhs"),
    ("释彩帛", "shi-ming/shi-cai-bo/zhs"),
    ("释首饰", "shi-ming/shi-shou-shi/zhs"),
    ("释衣服", "shi-ming/shi-yi-fu/zhs"),
    ("释宫室", "shi-ming/shi-gong-shi/zhs"),
    ("释床帐", "shi-ming/shi-chuang-zhang/zhs"),
    ("释书契", "shi-ming/shi-shu-qi/zhs"),
    ("释典艺", "shi-ming/shi-dian-yi/zhs"),
    ("释用器", "shi-ming/shi-yong-qi/zhs"),
    ("释乐器", "shi-ming/shi-yue-qi/zhs"),
    ("释兵", "shi-ming/shi-bing/zhs"),
    ("释车", "shi-ming/shi-che/zhs"),
    ("释船", "shi-ming/shi-chuan/zhs"),
    ("释疾病", "shi-ming/shi-ji-bing/zhs"),
    ("释丧制", "shi-ming/shi-sang-zhi/zhs"),
]

CTEXT_BOOKS = [
    {
        "filename": "03_名疑_陈士元.txt",
        "title": "名疑 (明 陈士元著, 四卷合集)",
        "url": "https://ctext.org/wiki.pl?if=gb&res=57819&remap=gb",
        "source": "中国哲学书电子化计划 (ctext.org)",
    },
    {
        "filename": "04_白虎通德论_姓名.txt",
        "title": "白虎通德论 - 姓名篇",
        "url": "https://ctext.org/bai-hu-tong/xing-ming/zhs",
        "source": "中国哲学书电子化计划 (ctext.org)",
    },
    {
        "filename": "05_潜夫论_志氏姓.txt",
        "title": "潜夫论 - 志氏姓篇",
        "url": "https://ctext.org/wiki.pl?chapter=811519&if=gb&remap=gb",
        "source": "中国哲学书电子化计划 (ctext.org)",
    },
]

MINGYI_CHAPTERS = [
    ("卷一", "https://ctext.org/wiki.pl?chapter=339696&if=gb&remap=gb"),
    ("卷二", "https://ctext.org/wiki.pl?chapter=136267&if=gb&remap=gb"),
    ("卷三", "https://ctext.org/wiki.pl?chapter=368036&if=gb&remap=gb"),
    ("卷四", "https://ctext.org/wiki.pl?chapter=324923&if=gb&remap=gb"),
]

UNAVAILABLE = [
    ("给孩子起个好名字", "李正明", "现代出版, 受版权保护, 请通过正规渠道购买"),
    ("中国姓名学", "高培淇", "现代出版, 受版权保护, 请通过正规渠道购买"),
    ("专业姓名学", "林鸿", "现代出版, 受版权保护, 请通过正规渠道购买"),
    ("姓名奇书大全", "刘溥麟", "现代出版, 受版权保护, 请通过正规渠道购买"),
    ("神松姓名学", "周神松", "现代出版, 受版权保护, 请通过正规渠道购买"),
    ("宝宝取名宝典 / 实用起名全书", "工具书", "现代出版, 受版权保护, 请通过正规渠道购买"),
    ("中华实用起名全解", "毛上文、毛业淳", "现代出版, 受版权保护, 请通过正规渠道购买"),
    ("慧缘姓名学", "慧缘", "现代出版, 受版权保护, 请通过正规渠道购买"),
]


def fetch_url(url: str, timeout: int = 120) -> str:
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text
        except Exception as exc:
            last_exc = exc
            print(f"    retry {attempt}/{MAX_RETRIES}: {exc}")
            time.sleep(REQUEST_DELAY * attempt)
    raise last_exc  # type: ignore[misc]


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


def write_book(path: Path, header: str, body: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"{header}\n\n{'=' * 50}\n\n{body}\n"
    path.write_text(content, encoding="utf-8")
    return len(body)


def format_shuowen_entry(data: dict) -> str:
    lines = [
        f"【{data.get('wordhead', '')}】",
        f"部首: {data.get('radical', '')} | 卷: {data.get('volume', '')} | 反切: {data.get('pronunciation', '')}",
        data.get("explanation", ""),
    ]
    for variant in data.get("variants") or []:
        lines.append(f"  重文 {variant.get('wordhead', '')}: {variant.get('explanation', '')}")
    if data.get("xuan_note"):
        lines.append(f"  徐铉注: {data['xuan_note']}")
    if data.get("kai_note"):
        lines.append(f"  徐锴注: {data['kai_note']}")
    for note in data.get("duan_notes") or []:
        exp = note.get("explanation", "")
        nt = note.get("note", "")
        if exp and nt:
            lines.append(f"  段注 [{exp}] {nt}")
        elif nt:
            lines.append(f"  段注: {nt}")
    return "\n".join(lines)


def ensure_shuowen_data() -> None:
    if SHUOWEN_DATA.is_dir():
        return
    clone_dir = SHUOWEN_DATA.parent
    print(f"Cloning shuowen data to {clone_dir} ...")
    clone_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", SHUOWEN_REPO, str(clone_dir)],
        check=True,
    )


def build_shuowen_txt() -> dict:
    out_path = OUT_DIR / "01_说文解字_许慎.txt"
    print("Building: 说文解字 (from shuowenjiezi/shuowen GitHub data)")

    ensure_shuowen_data()
    if not SHUOWEN_DATA.is_dir():
        raise FileNotFoundError(f"Shuowen data not found: {SHUOWEN_DATA}")

    entries: list[dict] = []
    for json_path in SHUOWEN_DATA.glob("*.json"):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(data, dict) and data.get("wordhead"):
            entries.append(data)

    entries.sort(key=lambda d: int(d.get("id", 0)))
    parts = [format_shuowen_entry(e) for e in entries]
    body = "\n\n".join(parts)
    header = (
        "书名: 说文解字 (东汉 许慎著, 含段玉裁注)\n"
        "来源: https://github.com/shuowenjiezi/shuowen (shuowen.org 公开数据)\n"
        f"条目数: {len(entries)}\n"
        f"整理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    chars = write_book(out_path, header, body)
    print(f"  -> saved {out_path.name} ({chars} chars, {len(entries)} entries)")
    return {"file": out_path.name, "status": "ok", "chars": chars}


def fetch_ctext_book(book: dict) -> dict:
    out_path = OUT_DIR / book["filename"]
    print(f"Fetching: {book['title']}")
    html = fetch_url(book["url"])
    body = parse_ctext_wiki(html)
    header = (
        f"书名: {book['title']}\n"
        f"来源: {book['source']}\n"
        f"URL: {book['url']}\n"
        f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    chars = write_book(out_path, header, body)
    print(f"  -> saved {out_path.name} ({chars} chars)")
    return {"file": book["filename"], "status": "ok", "chars": chars}


def parse_ctext_section(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    lines: list[str] = []
    title_el = soup.find("h2")
    if title_el:
        lines.append(title_el.get_text(strip=True))
        lines.append("-" * 30)

    tables = soup.find_all("table")
    for table in tables:
        for row in table.find_all("tr"):
            text = row.get_text(" ", strip=True)
            if text and "中国哲学书电子化计划" not in text:
                lines.append(text)

    if len(lines) <= 2:
        main = soup.find("div", id="content") or soup.body
        text = main.get_text("\n", strip=True) if main else ""
        return re.sub(r"\n{3,}", "\n\n", text)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def fetch_shiming() -> dict:
    out_path = OUT_DIR / "02_释名_刘熙.txt"
    print("Fetching: 释名 (二十七篇分章抓取)")
    parts: list[str] = []
    for chapter_name, path in SHIMING_CHAPTERS:
        url = f"https://ctext.org/{path}"
        print(f"  chapter: {chapter_name}")
        try:
            html = fetch_url(url)
            text = parse_ctext_section(html)
            parts.append(f"\n\n{'#' * 20}\n# {chapter_name}\n{'#' * 20}\n\n{text}")
        except Exception as exc:
            parts.append(f"\n\n# {chapter_name}\n[抓取失败: {exc}]")
        time.sleep(REQUEST_DELAY)

    body = "\n".join(parts).strip()
    header = (
        "书名: 释名 (东汉 刘熙著, 以声训解释名物, 二十七篇)\n"
        "来源: 中国哲学书电子化计划 (ctext.org)\n"
        f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    chars = write_book(out_path, header, body)
    print(f"  -> saved {out_path.name} ({chars} chars)")
    return {"file": out_path.name, "status": "ok", "chars": chars}


def fetch_mingyi_volumes() -> dict:
    out_path = OUT_DIR / "03_名疑_陈士元.txt"
    print("Fetching: 名疑 (四卷分章抓取)")
    parts: list[str] = []
    for vol_name, url in MINGYI_CHAPTERS:
        print(f"  chapter: {vol_name}")
        try:
            html = fetch_url(url)
            text = parse_ctext_wiki(html)
            parts.append(f"\n\n{'#' * 20}\n# {vol_name}\n{'#' * 20}\n\n{text}")
        except Exception as exc:
            parts.append(f"\n\n# {vol_name}\n[抓取失败: {exc}]")
        time.sleep(REQUEST_DELAY)

    body = "\n".join(parts).strip()
    header = (
        "书名: 名疑 (明 陈士元著, 四卷)\n"
        "来源: 中国哲学书电子化计划 (ctext.org)\n"
        f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    chars = write_book(out_path, header, body)
    print(f"  -> saved {out_path.name} ({chars} chars)")
    return {"file": out_path.name, "status": "ok", "chars": chars}


def write_index(results: list[dict]) -> None:
    index_path = OUT_DIR / "00_资料来源索引.txt"
    lines = [
        "起名相关典籍 - 资料来源索引",
        "=" * 50,
        f"整理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"存放目录: {OUT_DIR}",
        "",
        "一、已下载本地文件 (公开合法来源)",
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
            "二、对应用户书单说明",
            "",
            "【已获取 - 公开古籍/合法数据源】",
            "",
            "1. 《说文解字》 许慎 - 对应书单「形义分析根本依据」",
            "   本地文件: 01_说文解字_许慎.txt",
            "   在线: https://ctext.org/shuo-wen-jie-zi/zhs",
            "",
            "2. 补充古籍 (与起名文化相关, 公开来源):",
            "   - 02_释名_刘熙.txt (以声训释名, 起名音义参考)",
            "   - 03_名疑_陈士元.txt (古人姓名考证)",
            "   - 04_白虎通德论_姓名.txt (姓氏姓名源流)",
            "   - 05_潜夫论_志氏姓.txt (姓氏源流)",
            "",
            "【未能获取 - 现代版权图书】",
            "",
            "以下书目为现代出版物, 受著作权保护, 无法从公开网络",
            "合法下载全文。请通过书店、图书馆或正版电子书平台购买:",
            "",
        ]
    )
    for title, author, note in UNAVAILABLE:
        lines.append(f"- 《{title}》 {author} - {note}")

    lines.extend(
        [
            "",
            "三、获取建议",
            "",
            "- 现代姓名学著作可在京东/当当/微信读书等平台搜索书名购买",
            "- 若您已有纸质书或正版电子版, 可放入本目录供本地 RAG 使用",
            "- 公开古籍在线查阅: https://ctext.org  https://zh.wikisource.org",
            "",
            "四、技术说明",
            "",
            "- 说文解字数据来自 shuowenjiezi/shuowen (GitHub 开源数据)",
            "- 其他古籍来自 ctext.org 公开文本, 仅供个人学习研究",
        ]
    )
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Index saved: {index_path.name}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    try:
        results.append(build_shuowen_txt())
    except Exception as exc:
        results.append({"file": "01_说文解字_许慎.txt", "status": f"error: {exc}"})
        print(f"  -> FAILED shuowen: {exc}")

    try:
        results.append(fetch_shiming())
    except Exception as exc:
        results.append({"file": "02_释名_刘熙.txt", "status": f"error: {exc}"})
        print(f"  -> FAILED shiming: {exc}")

    for book in CTEXT_BOOKS:
        if book["filename"] == "03_名疑_陈士元.txt":
            continue
        try:
            results.append(fetch_ctext_book(book))
        except Exception as exc:
            results.append({"file": book["filename"], "status": f"error: {exc}"})
            print(f"  -> FAILED: {exc}")
        time.sleep(REQUEST_DELAY)

    try:
        results.append(fetch_mingyi_volumes())
    except Exception as exc:
        results.append({"file": "03_名疑_陈士元.txt", "status": f"error: {exc}"})
        print(f"  -> FAILED mingyi: {exc}")

    write_index(results)
    ok = sum(1 for r in results if r.get("status") == "ok")
    print(f"\nDone: {ok}/{len(results)} files saved to {OUT_DIR}")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
