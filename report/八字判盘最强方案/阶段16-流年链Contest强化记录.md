# 阶段16-流年链Contest强化记录

## 阶段目标

针对 contest 错因 `wrong_liunian` (14次, 仅次于调候) 强化流年岁运链, 将图谱流年规则、大运概览与判盘链岁运意见注入 DeepSeek MCQ prompt喵

## 本阶段变更

### 流年 Prompt 增强 (`liunian_context.py`)

- 扩展 `_needs_liunian_block`: 支持选项含年份、虚龄区间、婚姻/健康/官非/职业等主题触发
- 新增 `format_liunian_rules_block`: 按 `keys_liunian` 动态挂载 liunian 图谱规则与原文摘录
- 新增 `format_dayun_overview`: 结构化 MCQ 无目标年时仍输出大运概览
- 新增 `_suiyun_from_judgement`: 从判盘链提取 suiyun 裁判摘要
- `build_liunian_prompt_block` 新增参数 `options`, `judgement`, `force`

### Contest Prompt

- `build_contest_mcq_parts` 传入 options/judgement, 结构化推理时 `force=True` 强制流年块
- `LIUNIAN_EVENT_GUIDE` 补充须对照「流年岁运规则」与大运定位步骤

### 测试

- 新建 `tests/test_liunian_context_enhanced.py` (4项)

## 验证结果

| 验证项 | 结果 |
|--------|------|
| pytest liunian+tiaohou | 6 passed |
| contest 全量重跑 | 按用户要求跳过 |

## 对比阶段15

- 阶段15: 调候块注入 (tiaohou_context)
- 阶段16: 流年块增厚 (liunian rules + dayun overview + suiyun judgement)
- 二者在 contest prompt 中叠加: 调候 -> 流年时间轴/规则 -> 主题 guide

## 仍待深化

1. SuiYunJudge 尚未按题目主题动态挂载 liunian ruleIds (仅在 prompt 层补强)
2. 流年图谱仅 15 节点, 可继续从《三命通会》扩充 event 类规则
3. contest eval 全量对比留待用户需要时再跑

## 状态结论

**完成**. 流年链 Contest 强化已落地, 结构化 MCQ 将默认携带流年规则与大运概览, 无需全量评测即可进入下一阶段喵
