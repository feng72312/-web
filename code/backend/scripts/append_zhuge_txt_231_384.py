# -*- coding: utf-8 -*-
"""Append qian 231-384 to 数据库/12实用专区 秘本诸葛神数 txt for RAG."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).resolve().parents[1] / "data" / "zhuge_qian.json"
TXT = ROOT.parent / "数据库" / "12实用专区" / "秘本诸葛神数-三国蜀-诸葛亮.txt"


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    qian = payload["qian"]
    lines = ["", "", "  [签文补全 231-384]", ""]
    for num in range(231, 385):
        text = qian.get(str(num), "")
        if text:
            lines.append(f"  {num}。{text}")
    block = "\n".join(lines) + "\n"
    content = TXT.read_text(encoding="utf-8", errors="replace")
    if "[签文补全 231-384]" in content:
        head = content.split("  [签文补全 231-384]")[0].rstrip()
        TXT.write_text(head + block, encoding="utf-8")
    else:
        TXT.write_text(content.rstrip() + block, encoding="utf-8")
    print(f"appended {len(lines) - 4} lines to {TXT}")


if __name__ == "__main__":
    main()
