# Change: 修正 contest-benchmark 规格与实现对齐

## Why

变更 `improve-contest-accuracy-by-theme` 已归档, 但 `openspec/specs/contest-benchmark/spec.md` 仍描述旧行为 (如 static-light「仅单字母」「关闭结构化推理」), 与当前 `prompts_contest.py` / `mcq_reasoning_mode.py` 实现不一致。若不修正, 后续 P1-P4 任务会按错误规格验收或重复争论已落地设计。

## What Changes

- 更新 **Purpose**: 明确 contest-benchmark 规格描述大赛 MCQ 评测通道路由、prompt 与门禁, 而非排盘 API 本身。
- **MODIFIED** 通道路由: static-light 区分学历/家庭出身(轻量结构化)与子女(仍无完整流年块); 学历/家庭出身含年份选项时走题型专用 yingqi 变体。
- **ADDED** 静态题型 prompt 指南、题型纠偏、选项年份识别、子集 `--ids` 过滤等已实现能力。
- 补充 **已测子集基线** (文档性, 供后续变更引用), 不修改全量 200 门禁数字。
- **不修改** 运行时 Python 代码 (纯规格修正); 归档本变更后 `spec.md` 即为验收依据。

## Impact

- Affected specs: `contest-benchmark`
- Affected code: 无 (仅 OpenSpec 文档)
- 参考实现:
  - `code/backend/app/core/agent/prompts_contest.py`
  - `code/backend/app/core/knowledge/mcq_reasoning_mode.py`
  - `code/backend/app/core/knowledge/contest_channel_route.py`
  - `code/backend/app/core/knowledge/luck_prompt_util.py`
  - `code/backend/app/benchmark/contest8_rag.py`
  - `code/backend/app/core/knowledge/family_subtheme.py`
  - `code/backend/app/core/knowledge/family_option_scorer.py`
  - `code/backend/scripts/run_contest_theme_subset.py`

## 实测基线 (2026-06-15, 供对照)

| 子集 | 准确率 | 报告 |
|------|--------|------|
| 学历 (8题) | 6/8 = 75% | `contest8_sub_xueli_final.json` |
| 家庭出身 (14题) | 5/14 = 35.7% | `contest8_sub_jiating_ab2.json` |
| 学历+家庭 (22题) | 11/22 = 50% | 合计 |

当前保留实现为 **A+B** (子题型路由 + 家庭规则分); 方案 C/D/E (多票/加权投票/强化 death 打分) 已实验但未纳入基线.
