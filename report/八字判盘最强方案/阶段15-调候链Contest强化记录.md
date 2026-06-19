# 阶段15-调候链Contest强化记录

## 阶段目标

针对 contest 错因 `wrong_tiaohou` (15次) 优先强化调候链, 将《穷通宝鉴》结构化调候块注入 DeepSeek MCQ prompt, 并调整判盘预结论顺序喵

## 本阶段变更

### 调候 Prompt 模块

- 新建 `code/backend/app/core/knowledge/tiaohou_context.py`
- `build_tiaohou_prompt_block(chart, judgement, compressed)` 输出:
  - 日干/月支/ruleId
  - 调候摘要与原文摘录
  - 四柱透干对照
  - 用神提示(正则抽取先取/次用/得X逢/喜)
  - 断语边界

### Contest Prompt

- `prompts_contest.py` 注入 `tiaohou_note` (位于 reasoning guide 之后, 主题 guide 之前)
- `CONTEST_REASONING_GUIDE` 新增第 0 条: 先读穷通宝鉴调候
- `_format_judgement_block` 裁判意见按 tiaohou -> geju -> qishi -> shishen -> suiyun 排序

### 测试

- 新建 `tests/test_tiaohou_context.py`

## 验证

| 验证项 | 结果 |
|--------|------|
| pytest test_tiaohou_context | 2 passed |
| contest val smoke 5题 | 0/5 (样本过小, Q1-Q2 为 fallback 单字母解析, 不具统计意义) |

对比基线:
- geju_special_full 全量 40题: 35.0% (14/40)
- geju_special smoke 5题: 20.0% (1/5)
- tiaohou smoke 5题: 0.0% (0/5, 需全量重跑确认)

## 仍待深化

1. 用神提示正则仍粗, 可接图谱 claims 结构化字段
2. val 全量 40 题待重跑验证调候块收益
3. 流年错因 (wrong_liunian 14次) 仍为第二瓶颈

## 状态结论

**进行中**. 调候 Contest prompt 强化已落地; smoke 5题波动大, 建议下一步跑 val 全量 40 题对比 geju_special_full 基线喵
