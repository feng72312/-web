"""Ziwei source manifest: authority tiers and library separation."""

from __future__ import annotations

from pathlib import Path

SOURCE_CATEGORY = "11紫微斗数"

PALACE_TOPIC_FILES = {
    "兄弟宫论命要诀.doc": (["palace"], ["兄弟"], ["兄弟"]),
    "夫妻宫论命要诀.doc": (["palace"], ["夫妻"], ["夫妻"]),
    "奴仆宫（交友宫）论命要诀.doc": (["palace"], ["奴仆"], ["奴仆", "交友"]),
    "子女宫论命要诀.doc": (["palace"], ["子女"], ["子女"]),
    "官禄宫（事业宫）论命要诀.doc": (["palace"], ["官禄"], ["官禄", "事业"]),
    "父母宫（相貌宫）论命要诀.doc": (["palace"], ["父母"], ["父母"]),
    "田宅宫论命要诀.doc": (["palace"], ["田宅"], ["田宅"]),
    "疾厄宫论命要诀.doc": (["palace"], ["疾厄"], ["疾厄"]),
    "福德宫论命要诀.doc": (["palace"], ["福德"], ["福德"]),
    "财帛宫论命要诀.doc": (["palace"], ["财帛"], ["财帛"]),
    "迁移宫.doc": (["palace"], ["迁移"], ["迁移"]),
}

# relative path under 11紫微斗数/ -> tuple fields
# (classic, authorityTier, evidenceRole, libraryRole, judgmentPolicy, canJudge,
#  school, topicScope, domains, palaceScope, starScope, mutagenScope, limitScope)
ZIWEI_FILE_SPECS: dict[str, tuple] = {
    "S_核心法本/《太微賦》精解.doc": (
        "太微赋",
        "S",
        "primary_classic",
        "judge_library",
        "can_primary_judge_after_chunk_tag",
        True,
        "general",
        ["palace", "star", "pattern", "mutagen"],
        ["general", "palace", "star", "pattern"],
        [],
        [],
        ["mutagen"],
        ["limit"],
    ),
    "S_核心法本/紫微斗数全书-宋陈抟明潘希尹-维基文库全览.txt": (
        "紫微斗数全书",
        "S",
        "primary_classic_fulltext",
        "judge_library",
        "can_primary_judge_after_chunk_tag",
        True,
        "general",
        ["palace", "star", "pattern", "limit", "mutagen"],
        ["general", "palace", "star", "pattern", "limit"],
        [],
        [],
        ["mutagen"],
        ["limit", "decadal", "yearly"],
    ),
    "S_核心法本/紫微斗数-十八飞星照胆经-识典古籍.txt": (
        "十八飞星照胆经",
        "S",
        "early_flying_star_classic",
        "judge_library",
        "can_primary_judge_after_chunk_tag",
        True,
        "feixing",
        ["mutagen", "limit", "star"],
        ["feixing", "mutagen", "limit", "star"],
        [],
        [],
        ["mutagen"],
        ["limit", "decadal"],
    ),
    "A_系统教材/《紫微斗数命理学》2019最新版，289000字.doc": (
        "紫微斗数命理学",
        "A",
        "systematic_support",
        "judge_library",
        "can_secondary_judge",
        True,
        "general",
        ["palace", "star", "pattern", "mutagen", "limit"],
        ["general", "palace", "star", "pattern"],
        [],
        [],
        ["mutagen"],
        ["limit"],
    ),
    "A_系统教材/大德山人-紫微斗数精成（上下编）.doc": (
        "大德山人紫微斗数精成",
        "A",
        "systematic_support",
        "judge_library",
        "can_secondary_judge",
        True,
        "sanhe",
        ["palace", "star", "pattern", "mutagen", "limit"],
        ["sanhe", "palace", "star", "pattern"],
        [],
        [],
        ["mutagen"],
        ["limit"],
    ),
    "A_系统教材/紫微斗数全书（令东来，2018年出版）更新目录.doc": (
        "令东来紫微斗数全书",
        "A",
        "systematic_support",
        "judge_library",
        "can_secondary_judge",
        True,
        "general",
        ["palace", "star", "pattern", "mutagen"],
        ["general", "palace", "star"],
        [],
        [],
        ["mutagen"],
        ["limit"],
    ),
    "A_系统教材/紫微斗数命盘解析（令东来-2018年出版）.doc": (
        "令东来命盘解析",
        "A",
        "systematic_support",
        "judge_library",
        "can_secondary_judge",
        True,
        "general",
        ["palace", "star", "pattern", "case"],
        ["general", "palace", "star", "case"],
        [],
        [],
        ["mutagen"],
        ["limit"],
    ),
    "A_星曜格局/紫微命理之细论星情.doc": (
        "细论星情",
        "A",
        "star_judge",
        "judge_library",
        "can_secondary_judge",
        True,
        "general",
        ["star"],
        ["star"],
        [],
        ["major", "minor"],
        [],
        [],
    ),
    "A_星曜格局/紫微格局研究.doc": (
        "紫微格局研究",
        "A",
        "pattern_judge",
        "judge_library",
        "can_secondary_judge",
        True,
        "general",
        ["pattern"],
        ["pattern"],
        [],
        [],
        [],
        [],
    ),
    "A_星曜格局/诸星在命身及十二宫吉凶要诀.doc": (
        "诸星宫位要诀",
        "A",
        "star_palace_judge",
        "judge_library",
        "can_secondary_judge",
        True,
        "general",
        ["star", "palace"],
        ["star", "palace"],
        [],
        ["major"],
        [],
        [],
    ),
    "B_技法补充/命身遷宮主星互入的补充讲解.doc": (
        "命身迁移互入",
        "B",
        "modern_explanation",
        "support_library",
        "explain_only",
        False,
        "general",
        ["palace", "star"],
        ["palace", "star"],
        ["命宫", "身宫", "迁移"],
        [],
        [],
        [],
    ),
    "B_技法补充/干支.doc": (
        "干支基础",
        "B",
        "basic_reference",
        "support_library",
        "explain_only",
        False,
        "general",
        ["basic"],
        ["basic"],
        [],
        [],
        [],
        [],
    ),
    "B_技法补充/斗数【庖丁解牛】.doc": (
        "庖丁解牛",
        "B",
        "modern_explanation",
        "support_library",
        "explain_only",
        False,
        "general",
        ["general"],
        ["general"],
        [],
        [],
        [],
        [],
    ),
    "B_技法补充/紫薇斗数论命不求人.doc": (
        "论命不求人",
        "B",
        "modern_explanation",
        "support_library",
        "explain_only",
        False,
        "general",
        ["general"],
        ["general"],
        [],
        [],
        [],
        [],
    ),
    "D_待清洗/斗数阳宅风水.doc": (
        "斗数阳宅风水",
        "D",
        "cross_topic_reference",
        "excluded_or_pending",
        "exclude_from_core_judge",
        False,
        "general",
        ["cross_topic"],
        ["cross_topic"],
        [],
        [],
        [],
        [],
    ),
    "D_待清洗/获得美满姻缘的法门.doc": (
        "美满姻缘法门",
        "D",
        "low_signal_topic",
        "excluded_or_pending",
        "exclude_from_core_judge",
        False,
        "general",
        ["marriage"],
        ["marriage"],
        ["夫妻"],
        [],
        [],
        [],
    ),
}

for fname, (topics, domains, palaces) in PALACE_TOPIC_FILES.items():
    palace_label = palaces[0]
    ZIWEI_FILE_SPECS[f"C_宫位专题/{fname}"] = (
        f"{palace_label}论命要诀",
        "C",
        "palace_topic_support",
        "topic_library",
        "topic_only_no_global_judge",
        False,
        "general",
        topics,
        domains,
        palaces,
        [],
        [],
        [],
    )


def _extract_classic(filename: str) -> str:
    stem = Path(filename).stem
    for token in ("紫微斗数", "紫薇斗数", "论命要诀", "精解"):
        stem = stem.replace(token, "")
    return stem.strip(" -_（）()") or Path(filename).stem


def _normalize_rel(source_file: str) -> str:
    return source_file.replace("\\", "/").replace(".txt", ".doc")


def _infer_from_path(source_file: str) -> tuple:
    normalized = source_file.replace("\\", "/")
    lookup = _normalize_rel(normalized)
    if lookup in ZIWEI_FILE_SPECS:
        return ZIWEI_FILE_SPECS[lookup]
    if "/" in lookup:
        tail = lookup.split("/", 1)[1]
        if tail in ZIWEI_FILE_SPECS:
            return ZIWEI_FILE_SPECS[tail]
        if tail in PALACE_TOPIC_FILES:
            topics, domains, palaces = PALACE_TOPIC_FILES[tail]
            return (
                f"{palaces[0]}论命要诀",
                "C",
                "palace_topic_support",
                "topic_library",
                "topic_only_no_global_judge",
                False,
                "general",
                topics,
                domains,
                palaces,
                [],
                [],
                [],
            )

    classic = _extract_classic(source_file)
    if "飞星" in source_file or "照胆" in source_file:
        school = "feixing"
    elif "大德山人" in source_file:
        school = "sanhe"
    else:
        school = "general"

    if source_file.startswith("S_"):
        return (
            classic,
            "S",
            "primary_classic",
            "judge_library",
            "can_primary_judge_after_chunk_tag",
            True,
            school,
            ["general"],
            ["general"],
            [],
            [],
            [],
            [],
        )
    if source_file.startswith("A_"):
        return (
            classic,
            "A",
            "systematic_support",
            "judge_library",
            "can_secondary_judge",
            True,
            school,
            ["general"],
            ["general"],
            [],
            [],
            [],
            [],
        )
    if source_file.startswith("B_"):
        return (
            classic,
            "B",
            "modern_explanation",
            "support_library",
            "explain_only",
            False,
            school,
            ["general"],
            ["general"],
            [],
            [],
            [],
            [],
        )
    if source_file.startswith("C_"):
        return (
            classic,
            "C",
            "palace_topic_support",
            "topic_library",
            "topic_only_no_global_judge",
            False,
            school,
            ["palace"],
            ["palace"],
            [],
            [],
            [],
            [],
        )
    return (
        classic,
        "D",
        "low_trust",
        "excluded_or_pending",
        "exclude_from_core_judge",
        False,
        school,
        ["general"],
        ["general"],
        [],
        [],
        [],
        [],
    )


def source_type_for(authority_tier: str, source_file: str) -> str:
    if authority_tier in ("S", "A"):
        return "classic"
    if authority_tier == "B":
        return "modern_textbook"
    if authority_tier == "C":
        return "topic_notes"
    return "misc"


def build_file_manifest(source_file: str) -> dict:
    (
        classic,
        authority_tier,
        evidence_role,
        library_role,
        judgment_policy,
        can_judge,
        school,
        topic_scope,
        domains,
        palace_scope,
        star_scope,
        mutagen_scope,
        limit_scope,
    ) = _infer_from_path(source_file)

    can_override = authority_tier == "S" and evidence_role.startswith("primary")
    can_enter_production_rag = library_role in (
        "judge_library",
        "support_library",
        "topic_library",
    )

    return {
        "sourceCategory": SOURCE_CATEGORY,
        "sourceFile": source_file.replace("\\", "/"),
        "classic": classic,
        "authorityTier": authority_tier,
        "evidenceRole": evidence_role,
        "sourceType": source_type_for(authority_tier, source_file),
        "libraryRole": library_role,
        "school": school,
        "domains": domains,
        "topicScope": topic_scope,
        "palaceScope": palace_scope,
        "starScope": star_scope,
        "mutagenScope": mutagen_scope,
        "limitScope": limit_scope,
        "judgmentPolicy": judgment_policy,
        "canJudge": can_judge,
        "canOverride": can_override,
        "canEnterProductionRag": can_enter_production_rag,
        "readStatus": "ok",
        "notes": "",
    }


def validate_manifest_files(manifest_files: list[dict], source_dir: Path) -> list[str]:
    errors: list[str] = []
    expected_doc = set(ZIWEI_FILE_SPECS.keys())
    expected_txt = {key.replace(".doc", ".txt") for key in expected_doc}
    expected = expected_doc | expected_txt
    found: set[str] = set()
    for row in manifest_files:
        rel = str(row.get("sourceFile") or "").replace("\\", "/")
        if rel.startswith("_"):
            continue
        found.add(rel)
        full = source_dir / rel
        if not full.is_file():
            errors.append(f"missing file: {rel}")

    missing = expected - found
    for rel in sorted(missing):
        alt = rel.replace(".doc", ".txt") if rel.endswith(".doc") else rel.replace(".txt", ".doc")
        if alt not in found and not (source_dir / alt).is_file():
            errors.append(f"manifest missing entry: {rel}")

    extra = found - expected
    for rel in sorted(extra):
        if not rel.startswith("_") and rel.endswith((".txt", ".doc", ".docx")):
            base = _normalize_rel(rel)
            if base not in expected_doc:
                errors.append(f"unexpected manifest entry: {rel}")
    return errors
