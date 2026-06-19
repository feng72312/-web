"""Liuyao source manifest: authority tiers and three-library separation."""

from __future__ import annotations

from pathlib import Path

SOURCE_CATEGORY = "02六爻卜筮"

S_CLASSICS = frozenset({"增删卜易", "卜筮正宗", "黄金策", "卜筮全书"})

# relative path under 02六爻卜筮/ -> (classic, authorityTier, evidenceRole, libraryRole, judgmentPolicy, canJudge, topicScope, domains)
LIUYAO_FILE_SPECS: dict[str, tuple] = {
    "S_主裁经典/增删卜易--野鹤老人.txt": (
        "增删卜易",
        "S",
        "core_divination_judge",
        "judge_library",
        "can_primary_judge",
        True,
        ["yong_shen", "wang_shuai", "shi_ying", "dong_bian", "ying_qi"],
        ["yong_shen", "wang_shuai", "sheng_ke", "ying_qi", "case"],
    ),
    "S_主裁经典/卜筮正宗-清-王洪绪.txt": (
        "卜筮正宗",
        "S",
        "core_divination_judge",
        "judge_library",
        "can_primary_judge",
        True,
        ["casting", "yong_shen", "fei_fu", "xun_kong", "yue_po", "dong_bian"],
        ["casting", "yong_shen", "fei_fu", "xun_kong", "yue_po", "dong_bian"],
    ),
    "S_主裁经典/黄金策-明-刘基.txt": (
        "黄金策",
        "S",
        "classic_topic_judge",
        "judge_library",
        "can_primary_judge",
        True,
        ["topic_divination"],
        ["wealth", "career", "marriage", "illness", "travel", "topic_divination"],
    ),
    "S_主裁经典/卜筮全书-明-姚际隆.txt": (
        "卜筮全书",
        "S",
        "encyclopedic_judge",
        "judge_library",
        "can_primary_judge",
        True,
        ["general", "topic_divination"],
        ["general", "topic_divination"],
    ),
    "A_辅助经典/火珠林-宋-麻衣道者.txt": (
        "火珠林",
        "A",
        "early_source_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["casting", "general"],
        ["casting", "general"],
    ),
    "A_辅助经典/正易心法-宋-麻衣道者.txt": (
        "正易心法",
        "A",
        "early_source_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["casting", "general"],
        ["casting", "general"],
    ),
    "A_辅助经典/断易天机-明-佚名.txt": (
        "断易天机",
        "A",
        "method_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["general", "topic_divination"],
        ["general", "method"],
    ),
    "A_辅助经典/断易鬼灵经--佚名.txt": (
        "断易鬼灵经",
        "A",
        "method_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["general"],
        ["general", "method"],
    ),
    "A_辅助经典/易隐-清-曹九锡.txt": (
        "易隐",
        "A",
        "method_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["yong_shen", "wang_shuai", "dong_bian"],
        ["yong_shen", "wang_shuai", "method"],
    ),
    "A_辅助经典/易冒-清-程良玉.txt": (
        "易冒",
        "A",
        "method_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["yong_shen", "wang_shuai", "dong_bian"],
        ["yong_shen", "wang_shuai", "method"],
    ),
    "A_辅助经典/易林补遗-明-张世宝.txt": (
        "易林补遗",
        "A",
        "method_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["general", "dong_bian"],
        ["general", "method"],
    ),
    "A_辅助经典/周易尚占-元-李道纯.txt": (
        "周易尚占",
        "A",
        "yijing_divination_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["general"],
        ["yijing", "general"],
    ),
    "A_辅助经典/大易断例卜筮元龟目--.txt": (
        "卜筮元龟目",
        "A",
        "case_formula_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["case", "topic_divination"],
        ["case", "formula"],
    ),
    "B_现代技法/曲炜-六爻多重取象【虚拟宝库网www.xunibaoku.com】.txt": (
        "曲炜六爻取象",
        "B",
        "modern_image_support",
        "support_library",
        "explain_only",
        False,
        ["image", "general"],
        ["image", "general"],
    ),
    "B_现代技法/兴易梅花六爻.doc": (
        "兴易梅花六爻",
        "B",
        "modern_mixed_support",
        "support_library",
        "explain_only",
        False,
        ["mixed", "general"],
        ["mixed", "general"],
    ),
    "B_现代技法/曲炜-六爻详真【虚拟宝库网www.xunibaoku.com】.doc": (
        "曲炜六爻详真",
        "B",
        "modern_method_support",
        "support_library",
        "explain_only",
        False,
        ["method", "general"],
        ["method", "general"],
    ),
}


def _extract_classic(filename: str) -> str:
    for classic in sorted(S_CLASSICS, key=len, reverse=True):
        if classic in filename:
            return classic
    stem = Path(filename).stem.replace("·", "-").replace("．", ".")
    parts = [p.strip() for p in stem.split("-") if p.strip()]
    return parts[0] if parts else stem


def _infer_from_path(source_file: str) -> tuple:
    normalized = source_file.replace("\\", "/")
    if normalized in LIUYAO_FILE_SPECS:
        return LIUYAO_FILE_SPECS[normalized]
    if "/" in normalized:
        tail = normalized.split("/", 1)[1]
        if tail in LIUYAO_FILE_SPECS:
            return LIUYAO_FILE_SPECS[tail]

    classic = _extract_classic(source_file)
    if classic in S_CLASSICS:
        return (
            classic,
            "S",
            "core_divination_judge",
            "judge_library",
            "can_primary_judge",
            True,
            ["general"],
            ["general"],
        )
    if "曲炜" in source_file or "兴易" in source_file:
        return (
            classic,
            "B",
            "modern_method_support",
            "support_library",
            "explain_only",
            False,
            ["general"],
            ["general"],
        )
    return (
        classic,
        "A",
        "method_support",
        "judge_library",
        "can_secondary_judge",
        True,
        ["general"],
        ["general"],
    )


def source_type_for(authority_tier: str, source_file: str) -> str:
    if authority_tier in ("S", "A"):
        return "classic"
    if authority_tier == "B":
        return "modern_textbook"
    return "misc"


def build_file_manifest(source_file: str) -> dict:
    (
        classic,
        authority_tier,
        evidence_role,
        library_role,
        judgment_policy,
        can_judge,
        topic_scope,
        domains,
    ) = _infer_from_path(source_file)

    can_override = authority_tier == "S" and evidence_role == "core_divination_judge"
    can_enter_production_rag = library_role in ("judge_library", "support_library")

    return {
        "sourceCategory": SOURCE_CATEGORY,
        "sourceFile": source_file.replace("\\", "/"),
        "classic": classic,
        "authorityTier": authority_tier,
        "evidenceRole": evidence_role,
        "sourceType": source_type_for(authority_tier, source_file),
        "libraryRole": library_role,
        "domains": domains,
        "topicScope": topic_scope,
        "judgmentPolicy": judgment_policy,
        "canJudge": can_judge,
        "canOverride": can_override,
        "canEnterProductionRag": can_enter_production_rag,
        "readStatus": "ok",
        "notes": "",
    }


def validate_manifest_files(manifest_files: list[dict], source_dir: Path) -> list[str]:
    errors: list[str] = []
    expected = set(LIUYAO_FILE_SPECS.keys())
    found: set[str] = set()
    for row in manifest_files:
        rel = str(row.get("sourceFile") or "").replace("\\", "/")
        found.add(rel)
        full = source_dir / rel
        if not full.is_file():
            errors.append(f"missing file: {rel}")

    missing = expected - found
    extra = found - expected
    for rel in sorted(missing):
        errors.append(f"manifest missing entry: {rel}")
    for rel in sorted(extra):
        if rel not in expected:
            errors.append(f"unexpected manifest entry: {rel}")
    return errors
