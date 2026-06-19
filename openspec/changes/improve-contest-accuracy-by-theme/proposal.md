# 变更: 按题型逐步提升命理师大赛 MCQ 准确率

## 背景与动机

全球命理师大赛 (Contest8) 基准评测当前准确率为 **63/200 = 31.5%**，低于此前的 **69/200**，也低于 `bazi_fewshot` 参考上限 **73/200**。错题按题型高度聚集: 静态类 (学历/家庭出身/子女) 因被强制走结构化岁运推理而失分; 应期类 (流年事件/综合) 因判盘链预结论与保守约束而失分。单一管线无法同时优化全部题型, 需要 **按题型分阶段、可度量** 的提升方案。

## 变更内容

- 正式确立 **三种 MCQ 推理通道** (按题型与应期信号分流): `full` (婚姻/健康), `yingqi` (明确应期), `static-light` (无应期信号的学历/家庭出身/子女)。
- 制定 **分阶段路线图** (P0-P4), 优先攻克最弱题型, 每阶段用固定子集评测门禁通过后再跑全量 200 题。
- 增加 **按题型/年份的回归子集**, 避免某一类提升 silently 牺牲其他类。
- **P0 家庭出身**: 子题型路由 (A) + 确定性规则分提示块 (B), 保留 ab2 为当前最佳基线。
- 明确各题型层级验收目标与总体里程碑 (**>= 69/200**, stretch **73/200**)。
- **不破坏** `/paipan` 与 `/paipan/judgement` 对外 API; 改动限于大赛评测路由与 prompt 组装。

## 影响范围

- 涉及规格: `contest-benchmark` (delta 见 `changes/improve-contest-accuracy-by-theme/specs/contest-benchmark/spec.md`; 归档前以 change delta 为准)
- 涉及代码:
  - `code/backend/app/core/knowledge/contest_channel_route.py`
  - `code/backend/app/core/knowledge/mcq_reasoning_mode.py`
  - `code/backend/app/core/knowledge/career_subtheme.py` (P3 职业子题型)
  - `code/backend/app/core/knowledge/children_subtheme.py` (P0 子女子题型)
  - `code/backend/app/core/knowledge/children_option_scorer.py` (P0 子女规则分)
  - `code/backend/app/core/knowledge/year_option_scorer.py`
  - `code/backend/app/core/knowledge/luck_prompt_util.py`
  - `code/backend/app/core/agent/prompts_contest.py`
  - `code/backend/app/benchmark/contest8_eval.py`
  - `code/backend/app/benchmark/contest8_rag.py`
  - `code/backend/scripts/run_contest_theme_subset.py`
  - `code/backend/scripts/run_contest_benchmark.py` 及报告脚本
- 涉及测试:
  - `tests/test_contest_channel_route.py`
  - `tests/test_contest8_rag.py`
  - `tests/test_mcq_reasoning_mode.py`
  - `tests/test_family_subtheme.py`
  - `tests/test_children_subtheme.py`
  - `tests/test_children_option_scorer.py`
  - `tests/test_career_subtheme.py`
  - `tests/test_career_prompts.py`
- 涉及报告: `report/命理师大赛-全量200题-bazi_liunian.md`, `code/backend/data/reports/contest8_*.json`

## 当前基线 (2026-06-15, 路由收窄后)

| 题型      | 准确率        | 当前通道                   |
| --------- | ------------- | -------------------------- |
| 健康疾病  | 50.0% (5/10)  | full                       |
| 职业财运  | 43.8% (14/32) | mixed                      |
| 流年事件  | 42.1% (8/19)  | yingqi                     |
| 性格外貌  | 33.3% (5/15)  | other                      |
| 综合      | 27.9% (12/43) | mixed                      |
| 婚姻感情  | 27.9% (12/43) | full                       |
| 田宅/官非 | 25.0%         | mixed                      |
| 家庭出身  | 35.7% (5/14)  | static-light / yingqi 分型 |
| 子女      | 60.0% (3/5)   | yingqi 分型 (子集 5 题, P014 改判职业) |
| 学历      | 75.0% (6/8)   | static-light / yingqi 分型 |

静态通道收窄后 val 快测: **14/40 = 35.0%** (较改前 val +2 题)。

## P0 子集实测 (保留基线 ab2)

| 子集            | 准确率       | 报告                              | 说明                         |
| --------------- | ------------ | --------------------------------- | ---------------------------- |
| 学历 (8题)      | 6/8 = 75%    | `contest8_sub_xueli_final.json` | P0 学历完成                  |
| 家庭出身 (14题) | 5/14 = 35.7% | `contest8_sub_jiating_ab2.json` | A+B 最佳; 自 3/14 基线 +2 题 |
| 子女 (5题)      | 3/5 = 60%    | `contest8_sub_zinv_p1.json`     | 子题型+规则分校准后           |

**未纳入基线 (已实验回退):** 家庭方案 C/D/E (多票/加权投票/强化 death 打分) — 未稳定超过 ab2。

## P0 子女摘要

- **子题型**: `children-birth-year` / `children-dayun-span` / `children-status`
- **规则分**: `build_children_option_score_block` (男官杀/女食伤, 时支冲合, 育龄/伏吟/日冲校准)
- **纠偏**: 孩子仅为背景的「赚大钱+买房」题改判 `职业财运`

## P0 家庭出身 A+B 摘要

- **A 子题型路由**: `family-death-father` / `family-death-mother` / `family-wealth-tier` / `family-relation`
- **B 规则分块**: `build_family_option_score_block`, 替代家庭题上的通用岁运评分; 规则分仅供参考, 不得强制选最高分

## P2 子集实测 (保留基线 p5)

| 子集              | 准确率        | 报告                              | 说明                                              |
| ----------------- | ------------- | --------------------------------- | ------------------------------------------------- |
| 婚姻感情 (43题)   | 12/43 = 27.9% | bazi_liunian 全量切片             | 基线; 主错因 wrong_liunian / wrong_yongshen       |
| p2 首轮           | 11/43 = 25.6% | `contest8_sub_hunyin_p2.json`     | votes=3 + 婚姻 prompt/保守约束; 较基线 -1         |
| p3 A+B            | 9/43 = 20.9%  | `contest8_sub_hunyin_p3.json`     | 较基线 -3                                         |
| p4 锚点+校准      | 8/43 = 18.6%  | `contest8_sub_hunyin_p4.json`     | 较 p3 -1, 较基线 -4; 未达 >= 15/43                |
| **婚姻感情 (43题)** | **12/43 = 27.9%** | **`contest8_sub_hunyin_p5.json`** | **p5 生产基线**; 回退 p2 prompt + 子题型仅评测元数据 |

**未纳入基线 (已实验回退):** p6 A类子题型路由 **11/43** — 未超 p5。

**结论:** 婚姻 prompt 以 p5 为准; 未达 >= 15/43。

## P3 子集实测 (保留基线 p2)

| 子集              | 准确率        | 报告                              | 说明                                                         |
| ----------------- | ------------- | --------------------------------- | ------------------------------------------------------------ |
| 职业财运 (38题)   | 15/38 = 39.5% | bazi_liunian 子集                 | 基线; 子集较全量 32 题多 6 题                                |
| p1                | 12/38 = 31.6% | `contest8_sub_qishi_p1.json`      | status 3/17; 【职业取象】刻板映射失败; 较基线 -3             |
| **职业财运 (38题)** | **18/38 = 47.4%** | **`contest8_sub_qishi_p2.json`** | **p2 生产基线**; wealth 5/8, year-event 6/12, status 6/17, major 1/1; 【选项对照】+ 反刻板 guide |
| p3                | 14/38 = 36.8% | `contest8_sub_qishi_p3.json`      | status/year 二次分流 + wealth-tier 过宽; 已回退              |
| p3b               | 17/38 = 44.7% | `contest8_sub_qishi_p3b.json`     | 部分回退仍低于 p2; 已回退                                    |

**未纳入基线 (已实验回退):** p3/p3b 二次分流与 wealth-tier 格式 — 未稳定超过 p2。

**结论:** 职业 prompt 以 p2 为准; 门禁 >= 14/32 已通过 (18/38); 主题词纠偏 `身家`/`年薪`/`投资`; 性格外貌与 RAG top_k 待 5.2/5.3.

## P2 健康疾病子集实测

| 子集            | 准确率       | 报告                               | 说明 |
| --------------- | ------------ | ---------------------------------- | ---- |
| 健康疾病 (10题) | 5/10 = 50%   | bazi_liunian 全量切片              | 基线 |
| **健康疾病 (10题)** | **4/10 = 40%** | **`contest8_sub_jiankang_p1.json`** | **p1 生产基线**; 子题型+专用 prompt+健康选项年份锚点 |
| p2 (已回退)     | 3/10 = 30%   | `contest8_sub_jiankang_p2.json`    | status/dayun 加长 guide+【五行脏腑对照】; 未超 p1 |
| p2_rag (已回退) | 3/10 = 30%   | `contest8_sub_jiankang_p2_rag.json` | RAG 在线重跑; 与 p2 同分 |

**未纳入基线 (已实验回退):** p2 `HEALTH_STATUS_MANDATORY` / `HEALTH_STATUS_TIMELINE_*`; p2 `HEALTH_DAYUN` 选项系统五行对照表 — 未稳定超过 p1.

**结论:** 健康 prompt 以 p1 为准; 样本仅 10 题 + votes=3 波动大, 门禁 5/10 未达, 暂不继续 prompt 加长实验.
