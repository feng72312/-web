from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import shutil


ROOT = Path(r"d:\ZY\数据库")
SKIP_DIRS = {"01八字命理", "02六爻卜筮", "11紫微斗数"}
DECRYPT_SCRIPT = Path(
    r"C:\Users\liqingfeng\.cursor\skills\decrypt\scripts\file_decrypt.py"
)

DYNASTY_RE = re.compile(r"-(?:汉|三国|三国蜀|晋|南北朝|隋|唐|五代|宋|辽|金|元|明|清|周)-")

# Explicit S-tier classics per category (basename).
S_CLASSICS: dict[str, set[str]] = {
    "03梅花易学": {
        "梅花易数-宋-邵雍.txt",
        "皇极经世书-宋-邵雍.txt",
        "皇极经世-宋-邵雍.txt",
    },
    "04奇门遁甲": {
        "奇门遁甲统宗-三国蜀-诸葛亮.txt",
        "奇门遁甲秘笈大全-明-刘伯温.txt",
        "遁甲符应经-宋-杨维德.txt",
    },
    "05大六壬": {
        "六壬大全-明-郭载騋.txt",
        "六壬指南-明-陈公献.txt",
        "壬归-清-佚名.txt",
        "六壬断案-宋-邵彦和.txt",
        "六壬心镜-唐-徐道符.txt",
        "御定大六壬直指-佚名.txt",
        "六壬直指御定-清-佚名.txt",
    },
    "06风水堪舆": {
        "葬书-晋-郭璞.txt",
        "撼龙经-唐-杨筠松.txt",
        "疑龙经-唐-杨筠松.txt",
        "青囊奥语-唐-杨筠松.txt",
        "青囊序-唐-杨筠松.txt",
        "天玉经-唐-杨筠松.txt",
        "地理辨正-清-蒋大鸿.txt",
    },
    "07相术神相": {
        "神相全编-宋-陈抟.txt",
        "柳庄相法-明-袁珙.txt",
        "许负相法-汉-许负.txt",
        "冰鉴-清-曾国藩.txt",
    },
    "08择日历算": {
        "钦定协纪辨方书-清-梅毂成.txt",
        "五行大义-隋-萧吉.txt",
    },
    "09星命占验": {
        "开元占经-唐-瞿昙悉达.txt",
        "乙巳占-唐-李淳风.txt",
        "星学大成-明-万民英.txt",
    },
    "10杂占方术": {
        "灵棋经-汉-东方朔.txt",
        "推背图-唐-李淳风.txt",
    },
    "13塔罗占卜": {
        "韦特塔罗图钥-Waite-1911.txt",
        "托特之书牌义-Crowley-基线.txt",
    },
}

# Case/topic materials.
C_CASES: dict[str, set[str]] = {
    "03梅花易学": {
        "刀骨梅花-佚名.txt",
        "梅花基础及卦例-佚名.txt",
        "教你学梅花预测-佚名.txt",
        "心易密解——“读象法”-佚名.txt",
        "梅花观梅拆字数全集-佚名.txt",
        "梅花易数摘录集成-佚名.txt",
        "梅花易数课堂笔记.txt",
    },
    "05大六壬": {
        "六壬存验-清-吴师青.txt",
        "大六壬断案-佚名.txt",
    },
    "06风水堪舆": {
        "实战命例风水与疾病.doc",
    },
    "08择日历算": {
        "实战命例九十九 结婚择日.doc",
        "自在道人实战命例一百迁移坟墓择日.doc",
    },
}

# Low-signal or cross-topic.
D_EXCLUDE: dict[str, set[str]] = {
    "03梅花易学": {
        "梅花是蔷薇科李属的落叶乔木.doc",
        "白话易经+文档.doc",
        "系辞+文档.doc",
        "中国易学表述矛盾法则的命题【藏籍阁微信：13159996769】.doc",
    },
    "10杂占方术": {
        "辰州符咒大全--.txt",
    },
}

B_KEYWORDS = (
    "教材",
    "手册",
    "笔记",
    "预测",
    "揭秘",
    "现代",
    "实务",
    "技术",
    "讲解",
    "大全.doc",
    "韩海军",
    "藏籍阁",
    "虚拟宝库",
    "曲炜",
    "兴易",
    "真易",
    "玄门",
    "贺氏",
    "新编",
    "全解",
    "小手册",
    "课堂",
    "打印稿",
    "万物类象.doc",
    "起卦方法",
    "体用断卦",
    "整理打印",
    "实战命例",
)

# 12实用专区 keeps thematic folders; map folder to role.
SHIYONG_TOPICS = {
    "周公解梦": ("topic_library", "dream_topic"),
    "测字": ("topic_library", "cezi_topic"),
    "诸葛神数": ("topic_library", "zhuge_topic"),
    "起名": ("judge_library", "naming_classic"),
}


def is_already_organized(category_dir: Path) -> bool:
    markers = ("S_主裁经典", "A_辅助经典", "B_现代技法", "C_案例专题", "D_待清洗")
    return any((category_dir / m).exists() for m in markers)


def classify_file(category: str, rel_path: str) -> str:
    name = Path(rel_path).name
    if name in D_EXCLUDE.get(category, set()):
        return "D_待清洗"
    if name in S_CLASSICS.get(category, set()):
        return "S_主裁经典"
    if name in C_CASES.get(category, set()):
        return "C_案例专题"
    if name.endswith(".doc") or name.endswith(".docx"):
        if any(k in name for k in B_KEYWORDS):
            return "B_现代技法"
        if category == "03梅花易学":
            return "B_现代技法"
        if category == "06风水堪舆" and "实战" in name:
            return "C_案例专题"
        return "B_现代技法"
    if any(k in name for k in B_KEYWORDS):
        return "B_现代技法"
    if category == "05大六壬" and name.endswith("-佚名.txt"):
        if not DYNASTY_RE.search(name):
            return "B_现代技法"
    if DYNASTY_RE.search(name):
        return "A_辅助经典"
    if category == "13塔罗占卜" and name.startswith("00_"):
        return "A_辅助经典"
    if category == "13塔罗占卜":
        return "A_辅助经典"
    return "A_辅助经典"


def organize_category(category_dir: Path) -> dict:
    category = category_dir.name
    moved: list[dict[str, str]] = []
    skipped: list[str] = []
    collisions: list[str] = []
    counts: dict[str, int] = defaultdict(int)

    if category == "12实用专区":
        for topic, (role, _) in SHIYONG_TOPICS.items():
            topic_dir = category_dir / topic
            if topic_dir.is_dir():
                counts[topic] = len(list(topic_dir.glob("*")))
        return {
            "category": category,
            "mode": "thematic_existing",
            "moved": moved,
            "movedCount": 0,
            "skipped": skipped,
            "collisions": collisions,
            "subdirCounts": dict(counts),
        }

    if is_already_organized(category_dir):
        for sub in sorted(category_dir.iterdir()):
            if sub.is_dir() and sub.name[0] in "SABCD":
                counts[sub.name] = len(list(sub.glob("*")))
        return {
            "category": category,
            "mode": "already_organized",
            "moved": moved,
            "movedCount": 0,
            "skipped": ["already organized"],
            "collisions": collisions,
            "subdirCounts": dict(counts),
        }

    file_entries: list[tuple[Path, str]] = []
    for path in sorted(category_dir.rglob("*")):
        if not path.is_file() or path.name.startswith("_"):
            continue
        rel = path.relative_to(category_dir).as_posix()
        if "/" in rel:
            skipped.append(rel)
            continue
        file_entries.append((path, classify_file(category, rel)))

    for dest_name in sorted({d for _, d in file_entries}):
        (category_dir / dest_name).mkdir(parents=True, exist_ok=True)

    for src, dest_name in file_entries:
        dst = category_dir / dest_name / src.name
        if dst.exists():
            collisions.append(str(dst))
            continue
        shutil.move(str(src), str(dst))
        moved.append({"file": src.name, "to": dest_name})
        counts[dest_name] += 1

    return {
        "category": category,
        "mode": "organized",
        "moved": moved,
        "movedCount": len(moved),
        "skipped": skipped,
        "collisions": collisions,
        "subdirCounts": dict(counts),
    }


def write_manifest(category_dir: Path, report: dict) -> None:
    category = category_dir.name
    counts = report.get("subdirCounts", {})
    total = sum(counts.values()) if counts else report.get("movedCount", 0)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    lines = [
        f"# {category}文件分类清单",
        "",
        f"- 生成时间: {now} 喵",
        f"- 整理模式: {report.get('mode', 'organized')} 喵",
        f"- 资料文件数: {total} 喵",
        "",
        "## 分类总览",
        "",
        "| 分类 | 数量 | 说明 |",
        "| ------ | ------ | ------ |",
    ]

    desc = {
        "S_主裁经典": "S 主裁经典/核心法本",
        "A_辅助经典": "A 辅助经典/源流古籍",
        "B_现代技法": "B 现代技法/讲义笔记",
        "C_案例专题": "C 案例专题/实盘材料",
        "D_待清洗": "D 待清洗/低信跨题",
        "周公解梦": "主题专题/周公解梦",
        "测字": "主题专题/测字",
        "诸葛神数": "主题专题/诸葛神数",
        "起名": "主题专题/起名典籍",
    }
    for key in sorted(counts.keys()):
        lines.append(f"| {key} | {counts[key]} | {desc.get(key, key)} |")

    lines.extend(
        [
            "",
            "## 查看规则",
            "",
            "- `S` 可作为该门类主裁证据, 需按片段标注占法与主题 喵",
            "- `A` 作为经典辅助, 不可单独压过 `S` 主裁结论 喵",
            "- `B` 仅作现代解释和技法补充, 不得越权主裁 喵",
            "- `C` 仅作案例或主题辅助 喵",
            "- `D` 默认不进入生产证据链 喵",
            "",
            "## 本次整理结果",
            "",
            f"- 移动结果: {report.get('movedCount', 0)} 个文件 喵",
            f"- 冲突: {len(report.get('collisions', []))} 喵",
            f"- 跳过: {len(report.get('skipped', []))} 喵",
        ]
    )

    (category_dir / "_文件分类清单.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    (category_dir / "_整理结果.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> int:
    reports: list[dict] = []
    for category_dir in sorted(ROOT.iterdir()):
        if not category_dir.is_dir():
            continue
        if len(category_dir.name) < 2 or not category_dir.name[:2].isdigit():
            continue
        if category_dir.name in SKIP_DIRS:
            continue
        report = organize_category(category_dir)
        write_manifest(category_dir, report)
        reports.append(report)
        print(
            json.dumps(
                {
                    "category": report["category"],
                    "mode": report["mode"],
                    "movedCount": report["movedCount"],
                    "subdirCounts": report.get("subdirCounts", {}),
                },
                ensure_ascii=False,
            )
        )

    summary_path = ROOT / "_数据库整理汇总.json"
    summary_path.write_text(
        json.dumps(
            {
                "generatedAt": datetime.now().isoformat(timespec="seconds"),
                "skippedCategories": list(SKIP_DIRS),
                "reports": reports,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
