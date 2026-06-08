"""Category folders under 数据库 and Chroma collection names."""

from __future__ import annotations

from pathlib import Path

CATEGORIES: list[tuple[str, str]] = [
    ("01八字命理", "kb_01_bazi"),
    ("02六爻卜筮", "kb_02_liuyao"),
    ("03梅花易学", "kb_03_meihua"),
    ("04奇门遁甲", "kb_04_qimen"),
    ("05大六壬", "kb_05_liuren"),
    ("06风水堪舆", "kb_06_fengshui"),
    ("07相术神相", "kb_07_xiangshu"),
    ("08择日历算", "kb_08_zeri"),
    ("09星命占验", "kb_09_xingming"),
    ("10杂占方术", "kb_10_zazhan"),
    ("11紫微斗数", "kb_11_ziwei"),
    ("12实用专区", "kb_12_shiyong"),
    ("13塔罗占卜", "kb_13_tarot"),
]

FOLDER_TO_COLLECTION = dict(CATEGORIES)
COLLECTION_TO_FOLDER = {v: k for k, v in CATEGORIES}

DEFAULT_CATEGORY = "01八字命理"
DEFAULT_COLLECTION = FOLDER_TO_COLLECTION[DEFAULT_CATEGORY]

SKIP_DUPLICATE_NAMES = frozenset(
    {
        "三命通会-明-万民英.txt",
        "五行精纪-宋-廖中.txt",
        "兰台妙选-明-西窗老人.txt",
        "渊海子平-宋-徐子平.txt",
    }
)


def is_category_dir(path: Path) -> bool:
    return path.is_dir() and len(path.name) >= 2 and path.name[:2].isdigit()


def list_category_dirs(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        return []
    return sorted(d for d in source_dir.iterdir() if is_category_dir(d))


def folder_to_collection(folder_name: str) -> str:
    if folder_name in FOLDER_TO_COLLECTION:
        return FOLDER_TO_COLLECTION[folder_name]
    if folder_name in COLLECTION_TO_FOLDER:
        return folder_name
    raise KeyError(f"unknown category: {folder_name}")


def resolve_category(category: str | None) -> str | None:
    if not category:
        return None
    category = category.strip()
    if category in FOLDER_TO_COLLECTION:
        return FOLDER_TO_COLLECTION[category]
    if category in COLLECTION_TO_FOLDER:
        return category
    prefix = category[:2]
    for folder, coll in CATEGORIES:
        if folder.startswith(prefix):
            return coll
    raise KeyError(f"unknown category: {category}")


def legacy_target_folder(path: Path) -> str:
    name = path.name
    if "六爻" in name:
        return "02六爻卜筮"
    if "梅花" in name or "梅花" in path.parts:
        return "03梅花易学"
    if "奇门" in name:
        return "04奇门遁甲"
    if "六壬" in name or "壬占" in name or "壬归" in name:
        return "05大六壬"
    if "风水" in name or "堪舆" in name or "葬" in name:
        return "06风水堪舆"
    if "相法" in name or "相术" in name or "神相" in name:
        return "07相术神相"
    if "择日" in name or "协纪" in name or "历" in name:
        return "08择日历算"
    if "星" in name and ("占" in name or "命" in name):
        return "09星命占验"
    if "紫微" in name or "紫薇" in name or "斗数" in name:
        return "11紫微斗数"
    return "01八字命理"
