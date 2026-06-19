from __future__ import annotations

from typing import Any

from app.core.liuyao.judgement.judgement_models import (
    EvidenceRequest,
    LiuyaoJudgeVerdict,
)
from app.core.liuyao.judgement.wuxing import branch_element, element_relation


def _yong_shen_line(chart: dict[str, Any], yong_shen: dict[str, Any]) -> dict[str, Any] | None:
    pos = int(yong_shen.get("position") or 0)
    for line in chart.get("lines") or []:
        if int(line.get("position", 0)) == pos:
            return line
    return None


class WangShuaiJudge:
    def judge(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> LiuyaoJudgeVerdict:
        line = _yong_shen_line(chart, yong_shen)
        if not line:
            return LiuyaoJudgeVerdict(
                role="wang_shuai",
                summary="用神爻位无效, 无法论旺衰",
                stance="neutral",
                conclusionKind="insufficient_evidence",
                confidenceBand="weak",
            )
        kong_po = line.get("kongPoState") or {}
        yue_po = bool(kong_po.get("yuePo"))
        xun_kong = bool(kong_po.get("xunKong"))
        strength = str(line.get("lineStrength") or "neutral")
        month_jian = chart.get("monthJian", "")
        day_chen = chart.get("dayChen", "")
        branch = line.get("branch", "")
        parts = [
            f"用神第{line.get('position')}爻({branch})",
            f"月建{month_jian}下为{strength}",
            f"日辰{day_chen}",
        ]
        stance: str = "neutral"
        band = "medium"
        boundary = ""
        if strength == "strong" and not yue_po:
            stance = "favorable"
            band = "strong"
            parts.append("得月建之气偏旺")
        elif strength == "weak" or yue_po:
            stance = "unfavorable"
            band = "weak"
            if yue_po:
                parts.append("值月破, 力弱待填实或生扶")
                boundary = "月破不直接断凶, 须看填实、合会或原神扶助"
            else:
                parts.append("失令或受克, 用神偏弱")
        if xun_kong:
            parts.append("临旬空, 事多虚缓")
            if band == "strong":
                band = "medium"
        return LiuyaoJudgeVerdict(
            role="wang_shuai",
            classic="增删卜易",
            summary="; ".join(parts),
            stance=stance,
            ruleIds=["wang_shuai:yue_jian_ri_chen"],
            confidenceBand=band,
            flags={"yuePo": yue_po, "xunKong": xun_kong, "lineStrength": strength},
            boundary=boundary,
        )

    def evidence_request(
        self,
        chart: dict[str, Any],
        yong_shen: dict[str, Any],
    ) -> EvidenceRequest:
        ys = yong_shen.get("yongShen", "")
        return EvidenceRequest(
            ruleId="wang_shuai:yue_jian_ri_chen",
            topic="wang_shuai",
            classicWhitelist=["增删卜易", "卜筮正宗"],
            query=f"用神{ys} 旺衰 月建{chart.get('monthJian', '')} 旬空 月破",
        )


class ShengKeJudge:
    def judge(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> LiuyaoJudgeVerdict:
        ys_line = _yong_shen_line(chart, yong_shen)
        if not ys_line:
            return LiuyaoJudgeVerdict(
                role="sheng_ke",
                summary="缺少用神爻, 无法论生克",
                stance="neutral",
                conclusionKind="insufficient_evidence",
                confidenceBand="weak",
            )
        ys_pos = int(ys_line.get("position", 0))
        ys_elem = branch_element(str(ys_line.get("branch") or ""))
        ji_shen_hits: list[str] = []
        yuan_shen_hits: list[str] = []
        for line in chart.get("lines") or []:
            pos = int(line.get("position", 0))
            if pos == ys_pos:
                continue
            branch = str(line.get("branch") or "")
            elem = branch_element(branch)
            rel = element_relation(elem, ys_elem)
            liuqin = str(line.get("liuqin") or "")
            moving = "动" if line.get("isMoving") else "静"
            if rel == "controls":
                ji_shen_hits.append(f"第{pos}爻{liuqin}({branch}){moving}克用神")
            elif rel == "generates":
                yuan_shen_hits.append(f"第{pos}爻{liuqin}({branch}){moving}生用神")
        stance: str = "neutral"
        band: str = "medium"
        if ji_shen_hits and not yuan_shen_hits:
            stance = "unfavorable"
            band = "weak"
        elif yuan_shen_hits and not ji_shen_hits:
            stance = "favorable"
            band = "strong"
        elif ji_shen_hits and yuan_shen_hits:
            stance = "mixed"
            band = "medium"
        summary_parts = []
        if yuan_shen_hits:
            summary_parts.append("原神: " + ", ".join(yuan_shen_hits[:2]))
        if ji_shen_hits:
            summary_parts.append("忌神: " + ", ".join(ji_shen_hits[:2]))
        if not summary_parts:
            summary_parts.append("卦中无明显生克用神之爻")
        boundary = ""
        moving_ji = [h for h in ji_shen_hits if "动" in h]
        if moving_ji:
            boundary = "忌神发动克用神, 须与旺衰并论, 不可单断大凶"
        return LiuyaoJudgeVerdict(
            role="sheng_ke",
            classic="增删卜易",
            summary="; ".join(summary_parts),
            stance=stance,
            ruleIds=["sheng_ke:ji_yuan_shen"],
            confidenceBand=band,
            flags={"jiShen": ji_shen_hits, "yuanShen": yuan_shen_hits},
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> EvidenceRequest:
        return EvidenceRequest(
            ruleId="sheng_ke:ji_yuan_shen",
            topic="sheng_ke",
            classicWhitelist=["增删卜易"],
            query=f"用神{yong_shen.get('yongShen', '')} 原神 忌神 动爻生克",
        )


class DongBianJudge:
    def judge(
        self,
        chart: dict[str, Any],
        yong_shen: dict[str, Any],
        topic_id: str = "",
    ) -> LiuyaoJudgeVerdict:
        moving = list(chart.get("movingLines") or [])
        risk = chart.get("riskFlags") or {}
        ben_chong = bool(risk.get("benLiuChong"))
        bian_chong = bool(risk.get("bianLiuChong"))
        huitou_flags: list[str] = []
        for line in chart.get("lines") or []:
            if not line.get("isMoving"):
                continue
            target = line.get("dongBianTarget") or {}
            huitou = str(target.get("huitou") or "")
            if huitou:
                huitou_flags.append(f"第{line.get('position')}爻{huitou}")
        parts: list[str] = []
        if moving:
            parts.append(f"动爻{moving}")
        else:
            parts.append("无动爻, 以静卦论")
        if huitou_flags:
            parts.append(", ".join(huitou_flags))
        stance: str = "neutral"
        band: str = "medium"
        boundary = ""
        rule_ids = ["dong_bian:moving_change"]
        if ben_chong or bian_chong:
            parts.append("卦逢六冲")
            rule_ids.append("dong_bian:liu_chong")
            if topic_id in {"illness", "self_illness"}:
                boundary = "近病逢冲可速愈, 久病逢冲则凶, 须辨病程远近"
                stance = "mixed"
            else:
                stance = "unfavorable"
                boundary = "六冲主散动变化, 事多反复, 须结合用神旺衰"
        ys_pos = int(yong_shen.get("position") or 0)
        if ys_pos in moving:
            parts.append("用神发动, 事有主动变化")
            stance = "mixed" if stance == "neutral" else stance
        return LiuyaoJudgeVerdict(
            role="dong_bian",
            classic="卜筮正宗",
            summary="; ".join(parts),
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand=band,
            flags={
                "benLiuChong": ben_chong,
                "bianLiuChong": bian_chong,
                "movingLines": moving,
            },
            boundary=boundary,
        )

    def evidence_request(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> EvidenceRequest:
        ben = (chart.get("benGua") or {}).get("name", "")
        return EvidenceRequest(
            ruleId="dong_bian:moving_change",
            topic="dong_bian",
            classicWhitelist=["卜筮正宗", "增删卜易"],
            query=f"{ben} 动爻 变卦 六冲 回头生克",
        )


class ShiYingJudge:
    def judge(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> LiuyaoJudgeVerdict:
        shi_ying = chart.get("shiYing") or {}
        shi = int(shi_ying.get("shi") or 0)
        ying = int(shi_ying.get("ying") or 0)
        ys_pos = int(yong_shen.get("position") or 0)
        shi_line = next(
            (ln for ln in chart.get("lines") or [] if int(ln.get("position", 0)) == shi),
            None,
        )
        ying_line = next(
            (ln for ln in chart.get("lines") or [] if int(ln.get("position", 0)) == ying),
            None,
        )
        parts = [f"世爻第{shi}爻, 应爻第{ying}爻"]
        stance: str = "neutral"
        if ys_pos == shi:
            parts.append("用神持世, 事在身")
            stance = "favorable"
        elif ys_pos == ying:
            parts.append("用神在应, 事在对方")
        if shi_line and ying_line:
            shi_elem = branch_element(str(shi_line.get("branch") or ""))
            ying_elem = branch_element(str(ying_line.get("branch") or ""))
            rel = element_relation(shi_elem, ying_elem)
            if rel == "generates":
                parts.append("世生应, 我方付出较多")
            elif rel == "controls":
                parts.append("世克应, 我方占主动")
            elif rel == "controlled_by":
                parts.append("应克世, 对方压力大")
        return LiuyaoJudgeVerdict(
            role="shi_ying",
            classic="增删卜易",
            summary="; ".join(parts),
            stance=stance,
            ruleIds=["shi_ying:shi_ying_relation"],
            confidenceBand="medium",
        )

    def evidence_request(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> EvidenceRequest:
        return EvidenceRequest(
            ruleId="shi_ying:shi_ying_relation",
            topic="shi_ying",
            query="世应 用神 持世",
        )


class LiuShenJudge:
    def judge(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> LiuyaoJudgeVerdict:
        line = _yong_shen_line(chart, yong_shen)
        if not line:
            return LiuyaoJudgeVerdict(
                role="liu_shen",
                summary="六神辅助: 用神不明",
                stance="neutral",
                confidenceBand="weak",
                boundary="六神仅作辅助, 不得压过旺衰生克",
            )
        liushen = str(line.get("liushen") or "")
        hints = {
            "青龙": "多主喜庆、顺利",
            "朱雀": "主口舌、文书、信息",
            "勾陈": "主迟滞、田土、牵连",
            "螣蛇": "主虚惊、变化、缠绕",
            "白虎": "主凶险、疾病、伤灾",
            "玄武": "主暧昧、失窃、阴私",
        }
        hint = hints.get(liushen, "六神参考")
        return LiuyaoJudgeVerdict(
            role="liu_shen",
            classic="卜筮全书",
            summary=f"用神临{liushen}, {hint}",
            stance="neutral",
            ruleIds=["liu_shen:aux_only"],
            confidenceBand="weak",
            boundary="六神仅作辅助, 不得压过旺衰生克",
        )

    def evidence_request(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> EvidenceRequest:
        return EvidenceRequest(
            ruleId="liu_shen:aux_only",
            topic="liu_shen",
            evidenceRoles=["encyclopedic_judge"],
            query="六神 青龙 白虎 辅助",
            judgeOnly=False,
        )


class YingQiJudge:
    def judge(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> LiuyaoJudgeVerdict:
        line = _yong_shen_line(chart, yong_shen)
        if not line:
            return LiuyaoJudgeVerdict(
                role="ying_qi",
                summary="应期待用神定后再详",
                stance="neutral",
                confidenceBand="weak",
            )
        kong_po = line.get("kongPoState") or {}
        hints: list[str] = []
        if kong_po.get("xunKong"):
            hints.append("旬空则待填实、冲实或逢合之时应")
        if kong_po.get("yuePo"):
            hints.append("月破则待合破、填实之月应")
        moving = list(chart.get("movingLines") or [])
        if moving:
            hints.append(f"动爻{moving}发动, 应期多从动变、合冲之日推")
        if not hints:
            hints.append("用神不空不破, 可据生旺之时与合日推应期")
        return LiuyaoJudgeVerdict(
            role="ying_qi",
            classic="增删卜易",
            summary="; ".join(hints),
            stance="neutral",
            ruleIds=["ying_qi:kong_po_fill"],
            confidenceBand="medium",
            boundary="应期须与旺衰、吉凶并论, 不可单点日期",
        )

    def evidence_request(self, chart: dict[str, Any], yong_shen: dict[str, Any]) -> EvidenceRequest:
        return EvidenceRequest(
            ruleId="ying_qi:kong_po_fill",
            topic="ying_qi",
            classicWhitelist=["增删卜易"],
            query="应期 旬空 月破 填实",
        )
