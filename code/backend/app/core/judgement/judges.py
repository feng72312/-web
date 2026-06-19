from __future__ import annotations

from typing import Any

from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.geju_special import detect_geju_special_patterns
from app.core.knowledge.luck_chart import resolve_active_dayun, resolve_target_year
from app.core.knowledge.keys import (
    build_geju_aspect_key,
    build_geju_key,
    build_geju_special_key,
    build_qishi_key,
    build_suiyun_key,
    build_tiaohou_key,
    normalize_geju_name,
)
from app.core.knowledge.shishen_context import (
    build_shishen_lookup_keys,
    lookup_shishen_rows,
    normalize_shishen_label,
)
from app.core.knowledge.keys_liunian import resolve_event_liunian_categories, select_liunian_categories
from app.core.knowledge.keys_interactions import (
    build_interaction_key,
    collect_shensha_labels,
    detect_interaction_patterns,
    resolve_interaction_notes,
)
from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.month_strength import assess_month_strength
from app.core.knowledge.qishi_context import lookup_qishi_rows
from app.core.knowledge.tiaohou_context import lookup_tiaohou_rows
from app.core.knowledge.tiers import hit_to_public
from app.core.judgement.models import EvidenceRequest, JudgeVerdict


def _lookup_rule(topic: str, key_builder, chart: dict[str, Any]) -> tuple[str, list[str], str, str]:
    """Return summary, rule_ids, stance, boundary from knowledge graph."""
    service = get_knowledge_service()
    summary = ""
    rule_ids: list[str] = []
    stance = "conditional"
    boundary = ""
    if not service.enabled:
        return summary, rule_ids, stance, boundary
    try:
        key = key_builder(chart)
        rows = service.store.lookup(topic, key)
        if not rows:
            return summary, rule_ids, stance, boundary
        hit = hit_to_public(rows[0])
        summary = hit.summary
        rule_ids.append(hit.id)
        stance = "favorable" if hit.safeAutoAnswer else "conditional"
        if hit.claims:
            boundary = hit.claims[0].conclusion[:120]
    except ValueError:
        pass
    return summary, rule_ids, stance, boundary


def _month_zhi(chart: dict[str, Any]) -> str:
    return str((chart.get("pillars") or {}).get("month", {}).get("zhi") or "")


def _day_gan(chart: dict[str, Any]) -> str:
    return str(chart.get("dayMaster") or (chart.get("pillars") or {}).get("day", {}).get("gan") or "")


def _month_shishen(chart: dict[str, Any]) -> str:
    return str((chart.get("pillars") or {}).get("month", {}).get("shishenGan") or "")


class MonthStrengthJudge:
    role = "month"
    classic = "子平真诠"

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        service = get_knowledge_service()
        assessed = assess_month_strength(chart)
        summary = assessed["summary"]
        rule_ids = list(assessed["ruleIds"])
        stance = assessed["stance"]
        boundary = assessed["boundary"]
        conclusion_kind = "rule_derived"

        if service.enabled:
            node = service.store.get_by_id("geju:principle:month_yongshen")
            if node:
                hit = hit_to_public(node)
                rule_ids.append(hit.id)
                summary = f"{summary}; 月令用神: {hit.summary[:80]}"
                conclusion_kind = "classic_direct"
        return JudgeVerdict(
            role="month",
            classic=self.classic,
            summary=summary[:240],
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand="medium",
            conclusionKind=conclusion_kind,
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        month_zhi = _month_zhi(chart)
        day_gan = _day_gan(chart)
        assessed = assess_month_strength(chart)
        return EvidenceRequest(
            ruleId=assessed["ruleIds"][0],
            topic="geju",
            classicWhitelist=[self.classic],
            authorityTiers=["S"],
            evidenceRoles=["primary_judge", "geju_judge"],
            query=f"月令{month_zhi} 旺衰 通根 日主{day_gan} {assessed['body']}",
            judgeOnly=True,
        )


class TiaohouJudge:
    role = "tiaohou"
    classic = "穷通宝鉴"

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        service = get_knowledge_service()
        summary = "月令与调候待查"
        rule_ids: list[str] = []
        stance = "neutral"
        boundary = ""
        confidence = "medium"

        if service.enabled:
            try:
                rows = lookup_tiaohou_rows(chart)
                if rows:
                    hit = hit_to_public(rows[0])
                    summary = hit.summary
                    rule_ids.append(hit.id)
                    stance = "favorable" if hit.safeAutoAnswer else "conditional"
                    if hit.claims:
                        boundary = hit.claims[0].conclusion[:120]
                    confidence = "strong" if hit.safeAutoAnswer else "medium"
            except ValueError:
                pass

        return JudgeVerdict(
            role="tiaohou",
            classic=self.classic,
            summary=summary,
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand=confidence,
            conclusionKind="classic_direct" if rule_ids else "insufficient_evidence",
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        day_gan = _day_gan(chart)
        month_zhi = _month_zhi(chart)
        return EvidenceRequest(
            ruleId=f"tiaohou:{day_gan}:{month_zhi}",
            topic="tiaohou",
            sourceScope=["judge_library"],
            classicWhitelist=[self.classic],
            authorityTiers=["S"],
            evidenceRoles=["tiaohou_judge", "primary_judge"],
            query=f"日干{day_gan}月支{month_zhi} 调候 用神",
            judgeOnly=True,
        )


class GejuJudge:
    role = "geju"
    classic = "子平真诠"

    def _collect_geju_rules(self, chart: dict[str, Any]) -> tuple[str, list[str], str, str]:
        service = get_knowledge_service()
        if not service.enabled:
            return "", [], "conditional", ""

        month_ss = normalize_geju_name(_month_shishen(chart))
        summaries: list[str] = []
        rule_ids: list[str] = []
        boundary = ""

        try:
            core_rows = service.store.lookup("geju", build_geju_key(chart))
            if core_rows:
                hit = hit_to_public(core_rows[0])
                summaries.append(hit.summary)
                rule_ids.append(hit.id)
                if hit.claims:
                    boundary = hit.claims[0].conclusion[:120]
        except ValueError:
            pass

        for aspect in ("success", "failure", "rescue", "taboo"):
            rows = service.store.lookup("geju", build_geju_aspect_key(aspect))
            if not rows:
                continue
            hit = hit_to_public(rows[0])
            if hit.id not in rule_ids:
                rule_ids.append(hit.id)
            if not boundary and hit.claims:
                boundary = hit.claims[0].conclusion[:120]

        for pattern in detect_geju_special_patterns(chart):
            rows = service.store.lookup("geju", build_geju_special_key(pattern))
            if not rows:
                continue
            hit = hit_to_public(rows[0])
            if hit.id not in rule_ids:
                rule_ids.append(hit.id)

        if month_ss:
            yun_key = {
                "monthShishen": month_ss,
                "gejuName": month_ss,
                "aspect": "yun",
            }
            yun_rows = service.store.lookup("geju", yun_key)
            if yun_rows:
                yun_hit = hit_to_public(yun_rows[0])
                if yun_hit.id not in rule_ids:
                    rule_ids.append(yun_hit.id)

        summary = summaries[0] if summaries else ""
        stance = "favorable" if rule_ids else "conditional"
        return summary, rule_ids, stance, boundary

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        month_ss = _month_shishen(chart)
        graph_summary, rule_ids, stance, boundary = self._collect_geju_rules(chart)
        if graph_summary:
            summary = graph_summary
            conclusion_kind = "classic_direct"
            confidence = "strong" if rule_ids else "medium"
        else:
            summary = f"月令十神为{month_ss or '未知'}, 格局须结合透干与救应判断"
            rule_ids = [f"geju:month:{normalize_geju_name(month_ss)}"] if month_ss else []
            conclusion_kind = "rule_derived"
            confidence = "medium"
            boundary = boundary or "需结合透干、破格与救应, 不可单看月令十神下定论"
        return JudgeVerdict(
            role="geju",
            classic=self.classic,
            summary=summary,
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand=confidence,
            conclusionKind=conclusion_kind,
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        month_ss = normalize_geju_name(_month_shishen(chart))
        return EvidenceRequest(
            ruleId=f"geju:month:{month_ss}",
            topic="geju",
            classicWhitelist=[self.classic, "三命通会"],
            authorityTiers=["S", "A"],
            evidenceRoles=["geju_judge", "primary_judge", "secondary_support"],
            query=f"月令{month_ss} 格局 成败 破格 救应 取运",
            judgeOnly=True,
        )


class QiShiJudge:
    role = "qishi"
    classic = "滴天髓"

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        wx = chart.get("wuxingCount") or {}
        if not wx:
            return JudgeVerdict(
                role="qishi",
                classic=self.classic,
                summary="五行气势待查",
                conclusionKind="insufficient_evidence",
            )
        dominant = max(wx, key=wx.get)
        weakest = min(wx, key=wx.get)
        rows = lookup_qishi_rows(chart)
        summary = ""
        rule_ids: list[str] = []
        stance = "conditional"
        boundary = ""
        if rows:
            parts: list[str] = []
            for row in rows[:3]:
                hit = hit_to_public(row)
                if hit.id and hit.id not in rule_ids:
                    rule_ids.append(hit.id)
                if hit.summary:
                    parts.append(hit.summary)
                if hit.safeAutoAnswer and stance != "favorable":
                    stance = "favorable"
                if hit.claims and not boundary:
                    boundary = hit.claims[0].conclusion[:120]
            summary = "; ".join(parts[:2]) if parts else ""
        if summary:
            conclusion_kind = "classic_direct"
            confidence = "strong" if len(rule_ids) >= 2 else "medium"
        else:
            summary = f"五行偏{dominant}弱{weakest}, 须看清浊流通与偏枯"
            rule_ids = [f"qishi:dominant:{dominant}"]
            conclusion_kind = "rule_derived"
            confidence = "medium"
            boundary = boundary or "气势判断须与格局、调候互证"
        return JudgeVerdict(
            role="qishi",
            classic=self.classic,
            summary=summary,
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand=confidence,
            conclusionKind=conclusion_kind,
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        wx = chart.get("wuxingCount") or {}
        dominant = max(wx, key=wx.get) if wx else ""
        return EvidenceRequest(
            ruleId=f"qishi:dominant:{dominant}",
            topic="qishi",
            classicWhitelist=[self.classic],
            authorityTiers=["S", "A"],
            evidenceRoles=["qishi_judge", "primary_judge"],
            query=f"五行气势 清浊 流通 {dominant}",
        )


class ShiShenJudge:
    role = "shishen"
    classic = "渊海子平"

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        service = get_knowledge_service()
        pillars = chart.get("pillars") or {}
        parts = []
        for key in ("year", "month", "hour"):
            ss = pillars.get(key, {}).get("shishenGan")
            if ss:
                parts.append(f"{key}{ss}")
        rule_ids: list[str] = []
        summaries: list[str] = []
        boundary = "十神六亲须回归格局体用; 刑冲合害由合冲裁判, 不得越权定格局"

        if service.enabled:
            for row in lookup_shishen_rows(service.store, chart):
                hit = hit_to_public(row)
                rule_ids.append(hit.id)
                summaries.append(hit.summary)

        if summaries:
            summary = f"十神结构: {', '.join(parts)}; {summaries[0][:120]}"
            if len(summaries) > 1:
                summary = f"{summary}; 六亲: {summaries[1][:80]}"
            conclusion_kind = "classic_direct"
            confidence = "strong" if len(rule_ids) >= 2 else "medium"
            stance = "conditional"
        else:
            summary = "十神结构: " + (", ".join(parts) if parts else "待查")
            conclusion_kind = "rule_derived"
            confidence = "medium"
            stance = "neutral"

        return JudgeVerdict(
            role="shishen",
            classic=self.classic,
            summary=summary[:240],
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand=confidence,
            conclusionKind=conclusion_kind,
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        month_ss = normalize_shishen_label(_month_shishen(chart))
        gender = str(chart.get("gender") or chart.get("sex") or "")
        return EvidenceRequest(
            topic="shishen",
            classicWhitelist=[self.classic, "三命通会"],
            authorityTiers=["S", "A"],
            evidenceRoles=["shishen_judge", "primary_judge"],
            query=f"十神 六亲 {month_ss} {gender}".strip(),
        )


class SuiYunJudge:
    role = "suiyun"
    classic = "三命通会"

    SUIYUN_CATEGORIES = ("dayun_core", "suiyun_core")

    def _question_from_chart(self, chart: dict[str, Any]) -> str:
        return str(
            chart.get("judgementQuestion")
            or (chart.get("benchmarkMeta") or {}).get("question")
            or ""
        ).strip()

    def _append_lookup(
        self,
        rule_ids: list[str],
        topic: str,
        lookup_key: dict[str, str],
    ) -> str:
        service = get_knowledge_service()
        if not service.enabled:
            return ""
        rows = service.store.lookup(topic, lookup_key)
        if not rows:
            return ""
        hit = hit_to_public(rows[0])
        if hit.id not in rule_ids:
            rule_ids.append(hit.id)
        return hit.summary

    def _collect_suiyun_rules(self, chart: dict[str, Any]) -> tuple[str, list[str], str, str]:
        service = get_knowledge_service()
        if not service.enabled:
            return "", [], "conditional", ""

        question = self._question_from_chart(chart)
        summaries: list[str] = []
        rule_ids: list[str] = []
        boundary = ""
        event_summaries: list[str] = []

        try:
            rows = service.store.lookup("suiyun", build_suiyun_key(chart))
            if rows:
                hit = hit_to_public(rows[0])
                summaries.append(hit.summary)
                rule_ids.append(hit.id)
                if hit.claims:
                    boundary = hit.claims[0].conclusion[:120]
        except ValueError:
            pass

        for category in self.SUIYUN_CATEGORIES:
            self._append_lookup(rule_ids, "suiyun", {"category": category})

        for category in select_liunian_categories(question):
            summary = self._append_lookup(rule_ids, "liunian", {"category": category})
            if summary and not boundary:
                boundary = summary[:120]
            if category.startswith("event_") and summary:
                event_summaries.append(summary[:80])

        summary = summaries[0] if summaries else ""
        if event_summaries:
            theme = infer_question_theme(question) if question else "综合"
            summary = (
                f"{summary}; 题目主题{theme}: {'; '.join(event_summaries)}"
                if summary
                else f"题目主题{theme}: {'; '.join(event_summaries)}"
            )
        stance = "favorable" if rule_ids else "conditional"
        return summary, rule_ids, stance, boundary

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        dayun = chart.get("dayun") or []
        if not dayun:
            return JudgeVerdict(
                role="suiyun",
                classic=self.classic,
                summary="大运信息不足",
                conclusionKind="insufficient_evidence",
            )
        first = dayun[0]
        active = resolve_active_dayun(chart, resolve_target_year(chart)) or first
        graph_summary, rule_ids, stance, boundary = self._collect_suiyun_rules(chart)
        active_label = (
            f"第{active.get('index', '?')}运 {active.get('ganzhi', '')} "
            f"虚龄{active.get('startAge', '')}-{active.get('endAge', '')}岁"
        )
        if resolve_target_year(chart):
            active_label += f" (目标年{resolve_target_year(chart)})"
        if graph_summary:
            summary = f"{active_label}; {graph_summary}"
            conclusion_kind = "classic_direct"
            confidence = "strong" if len(rule_ids) >= 3 else "medium"
        else:
            summary = (
                f"{active_label}; 起运后该步大运须结合原局体用与流年引动"
            )
            rule_ids = rule_ids or [f"suiyun:ganzhi:{first.get('ganzhi', '')}"]
            conclusion_kind = "rule_derived"
            confidence = "medium"
            boundary = boundary or "岁运为应, 须先看原局体用再论引动"
        return JudgeVerdict(
            role="suiyun",
            classic=self.classic,
            summary=summary,
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand=confidence,
            conclusionKind=conclusion_kind,
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        dayun = chart.get("dayun") or []
        active = resolve_active_dayun(chart, resolve_target_year(chart))
        gz = str((active or (dayun[0] if dayun else {})).get("ganzhi") or "")
        question = self._question_from_chart(chart)
        theme = infer_question_theme(question) if question else ""
        event_cats = resolve_event_liunian_categories(question)
        event_hint = f" {theme} {' '.join(event_cats)}" if event_cats else ""
        return EvidenceRequest(
            topic="suiyun",
            classicWhitelist=[self.classic],
            authorityTiers=["S", "A"],
            evidenceRoles=["suiyun_judge", "primary_judge"],
            query=f"大运 {gz} 流年 岁运{event_hint}",
        )


class InteractionsJudge:
    role = "interactions"
    classic = "子平真诠"

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        service = get_knowledge_service()
        patterns = detect_interaction_patterns(chart)
        stem_notes, branch_notes = resolve_interaction_notes(chart)
        shensha = collect_shensha_labels(chart)
        rule_ids: list[str] = []
        summaries: list[str] = []
        boundary = "刑冲合害与神煞仅作辅助, 不得压过格局与调候用神"

        if service.enabled:
            for pattern in patterns:
                rows = service.store.lookup("interactions", build_interaction_key(pattern))
                if not rows:
                    continue
                hit = hit_to_public(rows[0])
                rule_ids.append(hit.id)
                summaries.append(hit.summary)

        parts: list[str] = []
        if stem_notes and stem_notes != "暂无":
            parts.append(f"天干: {stem_notes}")
        if branch_notes and branch_notes != "暂无":
            parts.append(f"地支: {branch_notes}")
        if shensha:
            parts.append(f"神煞: {'、'.join(shensha[:6])}")
        chart_summary = " | ".join(parts) if parts else "四柱合冲刑害与神煞未见显著信号"
        if summaries:
            summary = f"{chart_summary}; {summaries[0][:80]}"
        else:
            summary = chart_summary

        has_adverse = (
            "branch_chong" in patterns
            or "branch_hai" in patterns
            or "branch_xing" in patterns
        )
        has_support = "branch_he" in patterns or "stem_he" in patterns
        if has_adverse and not has_support:
            stance = "unfavorable"
        elif has_support and not has_adverse:
            stance = "favorable"
        else:
            stance = "conditional"

        return JudgeVerdict(
            role="interactions",
            classic=self.classic,
            summary=summary[:240],
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand="medium" if rule_ids else "weak",
            conclusionKind="classic_direct" if rule_ids else "rule_derived",
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        stem_notes, branch_notes = resolve_interaction_notes(chart)
        shensha = collect_shensha_labels(chart)
        query_bits = []
        if stem_notes and stem_notes != "暂无":
            query_bits.append(f"天干{stem_notes}")
        if branch_notes and branch_notes != "暂无":
            query_bits.append(f"地支{branch_notes}")
        if shensha:
            query_bits.append("神煞 " + " ".join(shensha[:4]))
        query = " ".join(query_bits) or "四柱 刑冲 合害 神煞"
        return EvidenceRequest(
            topic="interactions",
            sourceScope=["judge_library", "classic_library"],
            classicWhitelist=["子平真诠", "滴天髓", "神峰通考"],
            authorityTiers=["S", "A"],
            evidenceRoles=["secondary_support", "interactions_judge"],
            query=query,
            judgeOnly=True,
        )


class ComprehensiveJudge:
    role = "comprehensive"
    classic = "三命通会"

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        interactions = InteractionsJudge()
        inter_v = interactions.judge(chart)
        suiyun = SuiYunJudge()
        suiyun_v = suiyun.judge(chart)
        parts = []
        rule_ids: list[str] = []
        if inter_v.summary:
            parts.append(f"神煞合冲: {inter_v.summary}")
            rule_ids.extend(inter_v.ruleIds or [])
        if suiyun_v.summary:
            parts.append(f"岁运互证: {suiyun_v.summary}")
            rule_ids.extend((suiyun_v.ruleIds or [])[:2])
        summary = "; ".join(parts) if parts else "古法互证须与格局调候并列"
        return JudgeVerdict(
            role="comprehensive",
            classic=self.classic,
            summary=summary,
            stance="conditional",
            ruleIds=rule_ids[:4],
            confidenceBand="medium",
            conclusionKind="rule_derived" if rule_ids else "insufficient_evidence",
            boundary="综合裁判仅辅助, 不得压过调候格局主裁",
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        return EvidenceRequest(
            topic="suiyun",
            classicWhitelist=["三命通会", "神峰通考"],
            authorityTiers=["S", "A"],
            evidenceRoles=["secondary_support"],
            query="神煞 古法 岁运 互证",
            judgeOnly=True,
        )


class BaseJudge:
    role = "base"
    classic = "渊海子平"

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        shishen_judge = ShiShenJudge()
        shishen_v = shishen_judge.judge(chart)
        interactions = InteractionsJudge()
        inter_v = interactions.judge(chart)
        parts = []
        rule_ids: list[str] = []
        if shishen_v.summary:
            parts.append(shishen_v.summary)
            rule_ids.extend((shishen_v.ruleIds or [])[:3])
        if inter_v.summary and "神煞" not in inter_v.summary:
            parts.append(inter_v.summary)
            rule_ids.extend((inter_v.ruleIds or [])[:2])
        summary = "; ".join(parts[:2]) if parts else "十神六亲与刑冲合害须回归月令用神"
        return JudgeVerdict(
            role="base",
            classic=self.classic,
            summary=summary,
            stance=shishen_v.stance if shishen_v.summary else "conditional",
            ruleIds=rule_ids[:5],
            confidenceBand="medium",
            conclusionKind="rule_derived" if rule_ids else "insufficient_evidence",
            boundary="基础裁判解释象义, 不单独决定格局用神",
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        return EvidenceRequest(
            topic="shishen",
            classicWhitelist=["渊海子平", "三命通会"],
            authorityTiers=["S", "A"],
            evidenceRoles=["secondary_support"],
            query="十神 六亲 刑冲合害 基础象义",
            judgeOnly=True,
        )


class CaseReferenceJudge:
    role = "case"

    def judge(self, chart: dict[str, Any]) -> JudgeVerdict:
        return JudgeVerdict(
            role="case",
            classic="",
            summary="命例材料仅作象义参考, 不得越权决定格局与用神",
            stance="reference_only",
            confidenceBand="weak",
            conclusionKind="experience_reference",
            boundary="禁止把案例结论直接套用到当前命盘",
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        day_gan = _day_gan(chart)
        month_zhi = _month_zhi(chart)
        return EvidenceRequest(
            topic="case",
            libraryRoles=["experience_library"],
            authorityTiers=["C"],
            evidenceRoles=["case_reference"],
            query=f"命例 日主{day_gan} 月支{month_zhi} 结构相似",
            judgeOnly=False,
        )


ALL_JUDGES = [
    MonthStrengthJudge(),
    TiaohouJudge(),
    GejuJudge(),
    QiShiJudge(),
    ShiShenJudge(),
    BaseJudge(),
    SuiYunJudge(),
    InteractionsJudge(),
    ComprehensiveJudge(),
    CaseReferenceJudge(),
]

PRIMARY_JUDGES = [j for j in ALL_JUDGES if j.role != "case"]
