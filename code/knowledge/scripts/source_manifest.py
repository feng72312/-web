"""Bazi source manifest: three-library separation and authority tiers."""

from __future__ import annotations

from pathlib import Path

# S-level core classics (primary judges)
S_CLASSICS = frozenset(
    {
        "穷通宝鉴",
        "子平真诠",
        "滴天髓",
        "三命通会",
        "渊海子平",
    }
)

# A-level supplementary classics
A_CLASSICS = frozenset(
    {
        "五行精纪",
        "神峰通考",
        "珞琭子",
        "李虚中命书",
        "兰台妙选",
        "命理正宗",
        "三命指迷赋",
        "人伦大统赋",
        "乾元秘旨",
        "月谈赋",
    }
)

T1_PATTERNS = S_CLASSICS | A_CLASSICS

T2_PATTERNS = ("评注", "阐微", "补注", "千里命稿", "命理探源", "永乐百问")

T3_PATTERNS = (
    "命例",
    "详批",
    "答疑",
    "伤病残灾",
    "全部命例",
    "添情命理解读",
    "实战命理",
    "实战断",
    "段命",
)

T4_PATTERNS = (
    "讲义",
    "技巧",
    "如何读",
    "如何鉴别",
    "特训班",
    "论八字【",
    "虚拟宝库",
    "曲炜-我是",
)

TIER_TO_AUTHORITY = {
    "T1": "S",
    "T2": "A",
    "T3": "C",
    "T4": "D",
}


def _extract_classic(filename: str) -> str:
    for classic in sorted(S_CLASSICS | A_CLASSICS, key=len, reverse=True):
        if classic in filename:
            return classic
    stem = Path(filename).stem.replace("·", "-").replace("．", ".")
    parts = [p.strip() for p in stem.split("-") if p.strip()]
    return parts[0] if parts else stem


def classify_legacy_tier(name: str) -> str:
    for pattern in T4_PATTERNS:
        if pattern in name:
            return "T4"
    for pattern in T3_PATTERNS:
        if pattern in name:
            return "T3"
    for pattern in T2_PATTERNS:
        if pattern in name:
            return "T2"
    for pattern in T1_PATTERNS:
        if pattern in name:
            return "T1"
    if "曲炜" in name or "曲伟" in name:
        return "T3"
    if name.endswith((".txt", ".doc", ".docx")):
        return "T2"
    return "T4"


def authority_tier_for_classic(classic: str, legacy_tier: str) -> str:
    # 命例/讲义必须先于经典书名匹配, 避免「滴天髓全部命例」被抬成 S 主裁
    if legacy_tier == "T3":
        return "C"
    if legacy_tier == "T4":
        return "D"
    if classic in S_CLASSICS:
        return "S"
    if classic in A_CLASSICS:
        return "A"
    if legacy_tier == "T2":
        return "B"
    return "B"


def evidence_role_for(authority_tier: str, classic: str) -> str:
    if authority_tier == "S":
        if classic == "穷通宝鉴":
            return "tiaohou_judge"
        if classic == "子平真诠":
            return "geju_judge"
        if classic == "滴天髓":
            return "qishi_judge"
        if classic == "渊海子平":
            return "shishen_judge"
        if classic == "三命通会":
            return "suiyun_judge"
        return "primary_judge"
    if authority_tier == "A":
        return "secondary_support"
    if authority_tier == "B":
        return "modern_explanation"
    if authority_tier == "C":
        return "case_reference"
    return "low_trust"


def library_role_for(authority_tier: str) -> str:
    if authority_tier in ("S", "A", "B"):
        return "judge_library"
    if authority_tier == "C":
        return "experience_library"
    return "supplement_library"


def source_type_for(name: str, authority_tier: str) -> str:
    if authority_tier in ("S", "A"):
        return "classic"
    if "命例" in name or "详批" in name:
        return "case_study"
    if "讲义" in name or "技巧" in name:
        return "lecture"
    if authority_tier == "B":
        return "modern_textbook"
    return "misc"


def domains_for(classic: str, evidence_role: str) -> list[str]:
    mapping = {
        "tiaohou_judge": ["tiaohou", "yongshen"],
        "geju_judge": ["geju", "pattern"],
        "qishi_judge": ["qishi", "strength"],
        "shishen_judge": ["shishen", "liuqin"],
        "suiyun_judge": ["dayun", "liunian", "shensha"],
        "case_reference": ["case", "xiangyi"],
        "secondary_support": ["general"],
        "modern_explanation": ["general"],
        "low_trust": [],
        "primary_judge": ["general"],
    }
    return mapping.get(evidence_role, ["general"])


def build_file_manifest(source_file: str) -> dict:
    legacy_tier = classify_legacy_tier(source_file)
    classic = _extract_classic(source_file)
    authority_tier = authority_tier_for_classic(classic, legacy_tier)
    evidence_role = evidence_role_for(authority_tier, classic)
    library_role = library_role_for(authority_tier)
    source_type = source_type_for(source_file, authority_tier)
    can_judge = authority_tier in ("S", "A") and library_role == "judge_library"
    can_override = authority_tier == "S"
    can_enter_production_rag = library_role in ("judge_library", "experience_library")

    if evidence_role == "case_reference":
        judgment_policy = "case_only_no_judge"
    elif can_judge:
        judgment_policy = "can_primary_judge"
    elif authority_tier == "B":
        judgment_policy = "explain_only"
    else:
        judgment_policy = "exclude_or_low_trust"

    return {
        "sourceCategory": "01八字命理",
        "sourceFile": source_file,
        "classic": classic,
        "legacyTier": legacy_tier,
        "authorityTier": authority_tier,
        "evidenceRole": evidence_role,
        "sourceType": source_type,
        "libraryRole": library_role,
        "domains": domains_for(classic, evidence_role),
        "judgmentPolicy": judgment_policy,
        "canJudge": can_judge,
        "canOverride": can_override,
        "canEnterProductionRag": can_enter_production_rag,
        "notes": "",
    }
