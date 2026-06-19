from __future__ import annotations

from typing import Any

from app.core.liuyao.judgement.models import TopicResult
from app.core.liuyao.models import LIUQIN_NAMES, YongShenResult
from app.core.liuyao.yong_shen_rules import find_yong_shen_position

SHI_YONG_SHEN = "世爻"


class YongShenJudge:
    def judge(
        self,
        chart: dict[str, Any],
        question: str,
        topic: TopicResult | None = None,
    ) -> YongShenResult:
        return judge_yong_shen(chart, question, topic)


def _lines(chart: dict[str, Any]) -> list[dict[str, Any]]:
    return list(chart.get("lines") or [])


def _liuqin_on_chart(chart: dict[str, Any], liuqin: str) -> list[int]:
    if liuqin == SHI_YONG_SHEN:
        shi = int(chart.get("shiYing", {}).get("shi", 0) or 0)
        return [shi] if 1 <= shi <= 6 else []
    return [
        int(line["position"])
        for line in _lines(chart)
        if line.get("liuqin") == liuqin
    ]


def _resolve_yong_shen(
    chart: dict[str, Any],
    topic: TopicResult,
) -> tuple[str, int, str, float, list[str]]:
    candidates = [topic.candidate_yong_shen, *topic.alternate_yong_shen]
    boundaries: list[str] = []

    for liuqin in candidates:
        if liuqin == SHI_YONG_SHEN:
            positions = _liuqin_on_chart(chart, liuqin)
            if positions:
                pos = positions[0]
                line = next((ln for ln in _lines(chart) if int(ln.get("position", 0)) == pos), None)
                actual = str((line or {}).get("liuqin") or "兄弟")
                return (
                    actual,
                    pos,
                    f"占事归类为{topic.topic_label}, 取世爻(第{pos}爻,{actual})为用神",
                    min(0.92, topic.confidence + 0.05),
                    boundaries,
                )
            boundaries.append("世爻位无效, 尝试候选用神")
            continue

        if liuqin not in LIUQIN_NAMES:
            continue

        positions = _liuqin_on_chart(chart, liuqin)
        if positions:
            pos = positions[0]
            reason = f"占事归类为{topic.topic_label}, 取{liuqin}爻(第{pos}爻)为用神"
            if len(positions) > 1:
                boundaries.append(f"卦中{liuqin}爻多处, 先取第{pos}爻")
            return (
                liuqin,
                pos,
                reason,
                min(0.95, topic.confidence + 0.08),
                boundaries,
            )
        boundaries.append(f"卦中无{liuqin}爻, 用神不上卦")

    shi = int(chart.get("shiYing", {}).get("shi", 1) or 1)
    fallback_liuqin = "兄弟"
    pos = find_yong_shen_position(chart, fallback_liuqin)
    boundaries.append("候选用神均不上卦, 降级取兄弟并参考世位")
    return (
        fallback_liuqin,
        pos,
        f"占事归类为{topic.topic_label}, 用神不上卦, 暂取{fallback_liuqin}第{pos}爻",
        max(0.25, topic.confidence - 0.25),
        boundaries,
    )


def judge_yong_shen(
    chart: dict[str, Any],
    question: str,
    topic: TopicResult | None = None,
) -> YongShenResult:
    from app.core.liuyao.judgement.topic_judge import classify_topic

    topic_result = topic or classify_topic(question)
    yong_shen, position, reason, confidence, boundaries = _resolve_yong_shen(
        chart,
        topic_result,
    )
    if boundaries:
        reason = f"{reason}; {'; '.join(boundaries)}"

    return YongShenResult(
        yong_shen=yong_shen,
        position=position,
        reason=reason,
        source="rule",
        confidence=round(confidence, 2),
        topic_id=topic_result.topic_id,
        rule_id=topic_result.rule_id,
    )
