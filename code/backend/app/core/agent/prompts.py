from __future__ import annotations

import json
from typing import Any

from app.core.agent.interpret_style import (
    InterpretStyle,
    bazi_style_mode_block,
    plain_interpret_task_closing,
)

from app.core.agent.chat_scope import CHAT_SCOPE_GUARDRAIL
from app.core.knowledge.models import CompressedContext, KnowledgeHit


def _format_knowledge_hits(hits: list[KnowledgeHit]) -> str:
    if not hits:
        return "(暂无结构化典籍节点)"
    lines: list[str] = []
    for idx, hit in enumerate(hits, start=1):
        agreement = hit.agreementLevel
        safe = "可直引" if hit.safeAutoAnswer else "需结合论"
        lines.append(
            f"{idx}. [{hit.topic}/{agreement}/{safe}] {hit.summary}"
        )
        for claim in hit.claims[:2]:
            source = claim.classic or claim.sourceFile
            quote = claim.quote[:180]
            lines.append(f"   - [{source}] {quote}")
    return "\n".join(lines)


def _format_excerpts(excerpts: list[dict[str, str]]) -> str:
    if not excerpts:
        return "(暂无按需检索原文)"
    lines: list[str] = []
    for idx, item in enumerate(excerpts, start=1):
        source = item.get("source", "未知来源")
        excerpt = item.get("excerpt", "")
        lines.append(f"{idx}. [{source}] {excerpt}")
    return "\n".join(lines)


def _gender_label(gender: Any) -> str:
    if gender == 1:
        return "男"
    if gender == 0:
        return "女"
    return "未知"


def _format_sections(chart: dict[str, Any]) -> str:
    sections = chart.get("sections", [])
    if not sections:
        return "(暂无分析模块输出)"
    lines: list[str] = []
    for section in sections:
        section_id = section.get("id", "")
        name = section.get("name", section_id)
        data = section.get("data", {})
        lines.append(f"- {name}: {json.dumps(data, ensure_ascii=False)}")
    return "\n".join(lines)


def _format_judgement_report(report: dict[str, Any] | None) -> str:
    if not report:
        return "(暂无判盘链输出)"
    lines: list[str] = []
    for step in report.get("steps") or []:
        lines.append(f"- {step.get('label', '')}: {step.get('summary', '')}")
    arb = report.get("arbitration") or {}
    for verdict in arb.get("judgeOpinions") or []:
        if verdict.get("role") == "case":
            continue
        rule_ids = verdict.get("ruleIds") or []
        rule_hint = f" ruleIds={','.join(rule_ids)}" if rule_ids else ""
        lines.append(
            f"[{verdict.get('role')}/{verdict.get('classic')}{rule_hint}] {verdict.get('summary', '')}"
        )
    for conflict in arb.get("conflicts") or []:
        lines.append(f"冲突: {conflict}")
    for bound in arb.get("finalBoundaries") or []:
        lines.append(f"边界: {bound}")
    return "\n".join(lines) if lines else "(暂无判盘链输出)"


def build_chart_context(
    chart: dict[str, Any],
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    *,
    legacy_excerpts: list[dict[str, str]] | None = None,
    judgement_report: dict[str, Any] | None = None,
) -> str:
    inp = chart.get("input", {})
    pillars = chart.get("pillars", {})
    name = inp.get("name") or "未命名"
    gender = _gender_label(inp.get("gender"))
    hits = compressed.hits if compressed else []
    excerpts = rag_excerpts if rag_excerpts is not None else (legacy_excerpts or [])
    return (
        f"你是一位精通子平八字的命理师, 请基于以下结构化命盘资料作答.\n"
        f"要求: 只使用给定资料推理, 不要编造典籍出处; 用语清晰, 用中文回答; "
        f"争议条目须并列说明, 不可强行合一; "
        f"不得把命例经验当规则, 不得用低权重资料推翻主裁典籍; "
        f"推断现实事件时须结合大运流年与用神喜忌, 勿脱离命盘臆测; "
        f"解读中引用格局/调候/岁运/合冲刑害结论时, 应尽量对应判盘链中的 ruleId; "
        f"直接输出解读正文, 不要加 MODE 标记或 markdown 标题.\n\n"
        f"命主: {name}\n"
        f"性别: {gender}\n"
        f"日主: {chart.get('dayMaster')} ({chart.get('dayMasterWuxing')})\n"
        f"四柱: 年{pillars.get('year', {}).get('ganzhi', '')} "
        f"月{pillars.get('month', {}).get('ganzhi', '')} "
        f"日{pillars.get('day', {}).get('ganzhi', '')} "
        f"时{pillars.get('hour', {}).get('ganzhi', '')}\n"
        f"分析模块:\n{_format_sections(chart)}\n\n"
        f"判盘链与裁判意见:\n{_format_judgement_report(judgement_report)}\n\n"
        f"结构化典籍结论:\n{_format_knowledge_hits(hits)}\n\n"
        f"补充原文摘录:\n{_format_excerpts(excerpts)}"
    )


GENERAL_CHAT_SCENARIOS: dict[str, str] = {
    "general": "通用术数顾问",
    "choose_method": "选择术数",
    "prepare_question": "整理问事",
    "explain_terms": "解释术语",
    "review_result": "解读已有结果",
}


def build_general_chat_bootstrap(
    scenario: str,
    *,
    title: str | None = None,
    initial_prompt: str | None = None,
) -> str:
    label = GENERAL_CHAT_SCENARIOS.get(scenario, GENERAL_CHAT_SCENARIOS["general"])
    session_title = title or label
    scenario_hints = {
        "general": "以通用术数顾问身份接待用户, 先了解背景再给出建议.",
        "choose_method": "帮助用户根据问事性质选择合适术数(八字, 紫微, 六爻, 梅花, 奇门, 塔罗等), 说明各自适用场景.",
        "prepare_question": "帮助用户把模糊问题整理成适合排盘或起卦的清晰表述, 列出关键信息与问事焦点.",
        "explain_terms": "用通俗语言解释命理与术数术语, 可举例说明, 避免堆砌黑话.",
        "review_result": "引导用户粘贴或描述已有测算结果, 再给出解读思路与注意事项.",
    }
    scenario_hint = scenario_hints.get(
        scenario,
        "以通用术数顾问身份接待用户.",
    )

    lines = [
        "你是紫云命理天文馆的东方术数顾问.",
        f"当前会话场景: {session_title} ({scenario}).",
        scenario_hint,
        "你可解释八字, 紫微斗数, 六爻, 梅花易数, 奇门遁甲, 大六壬, 风水, 塔罗等东方与辅助术数.",
        "回答须务实, 不装神弄鬼, 不承诺绝对结果, 不替代专业判断.",
        "涉及医疗, 法律, 投资等重大决策时, 提醒用户咨询对应领域专业人士.",
        "先弄清用户背景与问事, 再建议合适术数或解读方向.",
        "语气亲切专业, 使用简体中文.",
    ]
    if initial_prompt:
        lines.append(f"用户可能首先关心: {initial_prompt}")
    lines.append(CHAT_SCOPE_GUARDRAIL)
    lines.append("以上是通用对话背景, 请等待用户提问.")
    return "\n".join(lines)


def build_chat_init_prompt(
    chart: dict[str, Any],
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    *,
    legacy_excerpts: list[dict[str, str]] | None = None,
) -> str:
    context = build_chart_context(
        chart,
        compressed=compressed,
        rag_excerpts=rag_excerpts,
        legacy_excerpts=legacy_excerpts,
    )
    return (
        f"{context}\n\n{CHAT_SCOPE_GUARDRAIL}\n\n"
        "以上是当前命盘背景资料, 请等待用户提问."
    )


def build_interpret_prompt(
    chart: dict[str, Any],
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    *,
    legacy_excerpts: list[dict[str, str]] | None = None,
    judgement_report: dict[str, Any] | None = None,
    style: InterpretStyle = "professional",
) -> str:
    context = build_chart_context(
        chart,
        compressed=compressed,
        rag_excerpts=rag_excerpts,
        legacy_excerpts=legacy_excerpts,
        judgement_report=judgement_report,
    )
    if style == "plain":
        task = (
            "请按上方四段式大纲, 输出一份从零基础读者视角可读的完整八字批命.\n"
            "不得改变判盘链预结论与用神喜忌方向, 仅改表述方式.\n"
            f"{plain_interpret_task_closing(1800)}"
        )
        reader_note = (
            "重要: 下方是后台专业资料, 请勿原文复述盘面术语与数据.\n\n"
        )
    else:
        task = (
            "请按上方四段式大纲, 输出一份可核对的专业八字批命.\n"
            "重点覆盖: 格局成败、体用喜忌、十神六亲、大运流年应期与趋避建议.\n"
            "控制在 2000 字以内.\n"
            "格式要求:\n"
            "1. 各大部分内按段落输出, 每段一个独立结论\n"
            "2. 凡引用判盘链或典籍规则, 必须在段末标注 [ruleId:xxx]\n"
            "3. 无规则支撑的推测须单独成段, 段首标注(推断), 且不得伪造 ruleId"
        )
        reader_note = ""
    return f"{reader_note}{context}\n\n{bazi_style_mode_block(style)}\n\n{task}"
