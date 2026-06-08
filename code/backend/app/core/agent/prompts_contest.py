from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.agent.prompts import _format_excerpts, build_chart_context
from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.liunian_context import (
    build_liunian_prompt_block,
    is_liunian_event_question,
)
from app.core.knowledge.mcq_reasoning_mode import (
    is_year_option_mcq,
    should_structured_mcq_reasoning,
)
from app.core.knowledge.option_exclusion import build_option_exclusion_block
from app.core.knowledge.models import CompressedContext
from app.core.knowledge.year_option_scorer import build_year_option_score_block

DEFAULT_FEWSHOT_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "contest8_fewshot.json"
)

CONTEST_REASONING_GUIDE = """
命理师大赛选择题作答要点:
1. 先定格局与体用, 再看日主强弱与用神喜忌, 勿脱离命盘臆测.
2. 问职业/财运/事业: 结合财星、官杀、食伤与大运流年, 看何运得助或受制.
3. 问婚姻/感情/子女: 看配偶星、桃花、合冲刑害, 及对应大运流年是否引动.
4. 问健康: 看五行偏枯、刑冲穿害, 对应脏腑与大运流年加重或缓解.
5. 问具体年份事件: 必须对照大运、流年与四柱作用, 勿只凭单柱或直觉.
6. 题目若给出虚龄或大限区间, 先用大运起运年龄换算到公历流年再判断.
7. 四选一须选最贴合命盘与运程的一项; 相近时选与用神/忌神作用最一致者.
""".strip()

LIUNIAN_EVENT_GUIDE = """
流年事件题: 必须用上文「流年时间轴」与「目标年结构化断语」中的目标年干支、十神、冲合.
官杀/七杀/伤官见官多关联官非压力; 偏财正财多关联财运而非必然横财; 印星受克多关联母亲健康文书; 食伤多关联变动口舌.
不得凭常识或常见叙事猜选, 须用命盘线索排除矛盾选项.
""".strip()

MARRIAGE_REASONING_GUIDE = """
婚姻感情题: 先看配偶星(财/官)在命局位置, 再看目标年流年是否合冲配偶宫.
已婚/离婚/外遇/子女数须与流年引动一致; 勿凭常见家庭叙事猜选.
""".strip()

HEALTH_REASONING_GUIDE = """
健康疾病题: 看五行偏枯、疾厄宫、官杀印与日主, 结合目标年冲合.
区分手术/住院/癌/骨折/慢性, 勿把财年冲一律断成重病.
""".strip()

GUANFEI_REASONING_GUIDE = """
官非题: 官杀、伤官见官、劫财逢冲多主压力与官非; 须对照选项中的牢狱/扣留/刑事关键词.
有财无官杀之年勿优先选横财或纯健康项.
""".strip()

LIUNIAN_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【目标年】
写出题干目标公历年、所在大运、流年干支、天干十神、关键冲合(来自上文排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用十神或冲合, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明为何剩余一项最贴合; 若两项仍接近, 写明差在哪及如何取舍.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()


def _format_options(options: list[str]) -> str:
    lines: list[str] = []
    for opt in options:
        letter = opt.strip()[:1].upper() if opt.strip() else "?"
        lines.append(f"{letter}. {opt}")
    return "\n".join(lines)


def _format_fewshot(examples: list[dict[str, Any]]) -> str:
    if not examples:
        return ""
    blocks: list[str] = ["参考范例(仅供推理方法, 勿照搬结论):"]
    for idx, ex in enumerate(examples, start=1):
        blocks.append(
            f"范例{idx}: 问: {ex.get('question', '')}\n"
            f"选: {ex.get('answer', '')} ({ex.get('answer_text', '')})"
        )
    return "\n".join(blocks)


def load_fewshot_examples(path: Path | None = None) -> list[dict[str, Any]]:
    p = path or DEFAULT_FEWSHOT_PATH
    if not p.is_file():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return list(data.get("examples") or [])


def _filter_fewshot(
    examples: list[dict[str, Any]],
    *,
    exclude_question_id: str | None,
    max_items: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ex in examples:
        if exclude_question_id and ex.get("question_id") == exclude_question_id:
            continue
        out.append(ex)
        if len(out) >= max_items:
            break
    return out


def build_contest_mcq_parts(
    chart: dict[str, Any],
    question: str,
    options: list[str],
    *,
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    fewshot_examples: list[dict[str, Any]] | None = None,
    current_question_id: str | None = None,
    use_option_elimination: bool | None = None,
) -> tuple[str, str]:
    context = build_chart_context(
        chart,
        compressed=compressed,
        rag_excerpts=[],
    )
    dayun_lines: list[str] = []
    from app.core.knowledge.luck_chart import get_dayun_timeline

    for d in get_dayun_timeline(chart):
        dayun_lines.append(
            f"第{d.get('index')}运 {d.get('ganzhi')} "
            f"虚龄{d.get('startAge')}-{d.get('endAge')} "
            f"起运年{d.get('startYear')}"
        )
    dayun_block = "\n".join(dayun_lines) if dayun_lines else "(无大运列表)"
    fs_list = _filter_fewshot(
        list(fewshot_examples or []),
        exclude_question_id=current_question_id,
        max_items=4,
    )
    # 流年专用 few-shot 易与通用范例冲突, 默认仅用通用 few-shot
    fewshot = _format_fewshot(fs_list)
    fewshot_block = f"\n\n{fewshot}" if fewshot else ""
    case_note = ""
    if rag_excerpts:
        case_note = (
            "\n\n命例讲解摘录(来自知识库RAG, 可参考同类命盘断法, 勿与当前命主混为一谈):\n"
            f"{_format_excerpts(rag_excerpts[:5])}"
        )
    is_event = is_liunian_event_question(question)
    if use_option_elimination is None:
        use_option_elimination = should_structured_mcq_reasoning(question, options)
    theme = infer_question_theme(question)
    liunian_block = build_liunian_prompt_block(chart, question, compressed)
    liunian_note = f"\n\n{liunian_block}" if liunian_block else ""
    exclusion_block = ""
    if use_option_elimination:
        excl = build_option_exclusion_block(chart, question, options)
        if excl:
            exclusion_block = f"\n\n{excl}"
    year_score_block = ""
    if use_option_elimination and is_year_option_mcq(options):
        ys = build_year_option_score_block(chart, question, options)
        if ys:
            year_score_block = f"\n\n{ys}"
    theme_guide = ""
    if theme == "婚姻感情":
        theme_guide = f"\n\n{MARRIAGE_REASONING_GUIDE}"
    elif theme == "健康疾病":
        theme_guide = f"\n\n{HEALTH_REASONING_GUIDE}"
    elif theme == "官非":
        theme_guide = f"\n\n{GUANFEI_REASONING_GUIDE}"
    event_guide = f"\n\n{LIUNIAN_EVENT_GUIDE}" if is_event else ""
    elimination_guide = (
        f"\n\n{LIUNIAN_REASONING_FORMAT}" if use_option_elimination else ""
    )
    system = (
        f"{context}\n\n"
        f"大运序列:\n{dayun_block}\n\n"
        f"{CONTEST_REASONING_GUIDE}"
        f"{theme_guide}"
        f"{event_guide}"
        f"{elimination_guide}"
        f"{liunian_note}"
        f"{exclusion_block}"
        f"{year_score_block}"
        f"{fewshot_block}"
        f"{case_note}"
    )
    if use_option_elimination:
        user = (
            f"命理师大赛四选一, 须先推理再作答.\n"
            f"题目: {question}\n"
            f"选项:\n{_format_options(options)}\n\n"
            f"须先读【规则预排除】, 再按格式完成【目标年】【选项排除】【结论】; "
            f"若推翻预排除须写明依据. 最后一行写「答案:」+ 一个字母."
        )
    else:
        user = (
            f"请回答以下命理师大赛四选一题目.\n"
            f"题目: {question}\n"
            f"选项:\n{_format_options(options)}\n\n"
            f"要求: 只输出一个大写字母 A/B/C/D (若选项为小写 a/b/c/d 则输出对应小写), "
            f"不要输出解释、标点或其他文字."
        )
    return system, user


def _ziwei_palace_lines(palaces: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for palace in palaces[:12]:
        major = "、".join(s.get("name", "") for s in palace.get("majorStars") or [])
        minor = "、".join(s.get("name", "") for s in (palace.get("minorStars") or [])[:4])
        lines.append(
            f"{palace.get('name', '')} {palace.get('stemBranch', '')} "
            f"主星:{major or '无'} 辅星:{minor or '无'} "
            f"大限:{palace.get('decadalRange', '')}"
        )
    return "\n".join(lines) or "(无宫位)"


ZIWEI_CONTEST_GUIDE = """
紫微斗数大赛四选一要点:
1. 先看命宫、身宫、三方四正主星与亮度, 定体性.
2. 问婚姻看夫妻宫, 问事业看官禄宫, 问财看财帛, 问健康看疾厄, 问子女看子女宫.
3. 题干若含公历年份, 须结合该年流年/大限/小限飞宫与四化.
4. 四选一选与盘象及流年最贴合的一项, 勿凭常识臆测.
""".strip()


def build_contest_ziwei_mcq_parts(
    ziwei_chart: dict[str, Any],
    question: str,
    options: list[str],
    *,
    rag_excerpts: list[dict[str, str]] | None = None,
) -> tuple[str, str]:
    meta = ziwei_chart.get("meta") or {}
    limits = ziwei_chart.get("limits") or {}
    excerpt_block = _format_excerpts(rag_excerpts or [])
    system = (
        f"你是紫微斗数专家, 按南派三合盘断四选一.\n"
        f"{ZIWEI_CONTEST_GUIDE}\n\n"
        f"真太阳时: {ziwei_chart.get('trueSolarTime', '')}\n"
        f"四柱: {ziwei_chart.get('fourPillars', {})}\n"
        f"局数: {meta.get('bureau', '')} 命主:{meta.get('soul', '')} "
        f"身主:{meta.get('body', '')} 生肖:{meta.get('zodiac', '')}\n"
        f"十二宫:\n{_ziwei_palace_lines(ziwei_chart.get('palaces') or [])}\n\n"
        f"大限序列: {limits.get('decadal', [])}\n"
        f"流年: {limits.get('yearly', {})}\n"
        f"当前大限/小限: {limits.get('current', {})}\n\n"
        f"紫微典籍摘录:\n{excerpt_block}"
    )
    user = (
        f"命理师大赛四选一, 问事: {question}\n"
        f"选项:\n{_format_options(options)}\n\n"
        f"要求: 只输出一个大写字母 A/B/C/D (小写选项则输出 a/b/c/d), 不要解释."
    )
    return system, user


def build_contest_liuyao_mcq_parts(
    liuyao_chart: dict[str, Any],
    yong_shen: dict[str, Any],
    question: str,
    options: list[str],
    *,
    rag_excerpts: list[dict[str, str]] | None = None,
) -> tuple[str, str]:
    ben = liuyao_chart.get("benGua", {}) or {}
    lines = liuyao_chart.get("lines", []) or []
    line_text = "\n".join(
        f"第{item.get('position')}爻 {item.get('stem', '')}{item.get('branch', '')} "
        f"{item.get('liuqin', '')} {item.get('liushen', '')}"
        f"{' 世' if item.get('isShi') else ''}"
        f"{' 应' if item.get('isYing') else ''}"
        f"{' 动' if item.get('isMoving') else ''}"
        for item in lines
    )
    excerpt_block = _format_excerpts(rag_excerpts or [])
    system = (
        f"你是六爻纳甲专家, 按《增删卜易》思路占断四选一, 结合月建日辰、世应、动爻生克.\n"
        f"起卦: {liuyao_chart.get('meta', {}).get('castNote', '')}\n"
        f"本卦: {ben.get('name', '')} 变卦: {(liuyao_chart.get('bianGua') or {}).get('name', '无')}\n"
        f"动爻: {liuyao_chart.get('movingLines', [])}\n"
        f"月建: {liuyao_chart.get('monthJian', '')} 日辰: {liuyao_chart.get('dayChen', '')}\n"
        f"用神: {yong_shen.get('yongShen', '')} (第{yong_shen.get('position', '')}爻)\n"
        f"六爻:\n{line_text}\n\n"
        f"六爻典籍摘录:\n{excerpt_block}"
    )
    user = (
        f"命理师大赛四选一, 问事: {question}\n"
        f"选项:\n{_format_options(options)}\n\n"
        f"要求: 只输出一个大写字母 A/B/C/D (小写选项则输出 a/b/c/d), 不要解释."
    )
    return system, user


def build_bazi_ziwei_arbitrate_parts(
    question: str,
    options: list[str],
    bazi_letter: str,
    ziwei_letter: str,
    *,
    bazi_note: str = "",
    ziwei_note: str = "",
) -> tuple[str, str]:
    system = (
        "你是命理师大赛仲裁员. 八字与紫微两通道对同一四选一给出不同字母时, "
        "须结合题干与选项, 判断哪一通道更符合题意, 只输出最终字母."
    )
    user = (
        f"题目: {question}\n"
        f"选项:\n{_format_options(options)}\n\n"
        f"八字通道答案: {bazi_letter or '无'}\n"
        f"八字要点: {(bazi_note or '(无)')[:400]}\n\n"
        f"紫微通道答案: {ziwei_letter or '无'}\n"
        f"紫微要点: {(ziwei_note or '(无)')[:400]}\n\n"
        f"要求: 只输出一个大写字母 A/B/C/D, 不要解释."
    )
    return system, user


def build_contest_mcq_prompt(
    chart: dict[str, Any],
    question: str,
    options: list[str],
    *,
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    fewshot_examples: list[dict[str, Any]] | None = None,
) -> str:
    system, user = build_contest_mcq_parts(
        chart,
        question,
        options,
        compressed=compressed,
        rag_excerpts=rag_excerpts,
        fewshot_examples=fewshot_examples,
    )
    return f"{system}\n\n{user}"
