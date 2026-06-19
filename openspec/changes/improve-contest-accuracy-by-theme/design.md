## 背景

Contest8 评测在 `contest8_eval.py` 的 `predict_one` 中完成: 经 `PaipanEngine` 排盘, 可选运行 `BaziJudgementChain`, 拉取知识图谱/RAG 上下文, 再调用 DeepSeek 输出 MCQ 选项字母。Prompt 组装在 `prompts_contest.py`; 题型分类在 `contest8_rag.py` 的 `infer_question_theme`。

近期实验结论:
- 全量判盘链对婚姻/健康有帮助, 但保守约束与错误的岁运/用神预结论会伤害应期题。
- 学历/家庭出身/子女等静态题, 在无明确年份时被强制结构化流年推理会退步。
- 虚龄/大运锚点块可减少应期题的大运区间换算错误。

## 目标 / 非目标

**目标:**
- 按题型分阶段提升 Contest8 总准确率, 每阶段有可度量门禁。
- 婚姻感情、健康疾病保持全量判盘链 (`full` 通道)。
- 应期题走轻量 `yingqi` prompt, 附带结构化大运/流年锚点。
- 无明确应期的学历/家庭出身走 `static-light`, 使用题型专用轻量结构化格式 (非完整流年块); 子女仍保持最轻单字母作答。
- 学历/家庭出身在选项含年份时走题型专用 yingqi 变体 (非泛应期格式)。
- 全量 200 题跑分前, 先用可复现的子集 (按题型/val/年份切片) 验证。

**非目标:**
- 本变更内不修改 PaipanEngine 四柱/大运计算规则 (除非某题型门禁证明排盘本身有错)。
- 不涉及紫微/六爻/融合通道。
- 不做模型训练或微调; 仅调整路由、prompt 与证据检索策略。

## 技术决策

### 决策 1: 四通道路由

| 通道 | 题型 / 触发条件 | 判盘链 | 命例 RAG | Prompt 风格 |
|------|----------------|--------|----------|-------------|
| `full` | 婚姻感情、健康疾病 (始终) | 是 | 是 | 结构化 + 保守约束 |
| `yingqi` | 明确应期信号 或 流年事件; 学历/家庭含年份选项时用专用变体 | 否 | 否 | 通用应期格式 + 虚龄锚点, 或题型专用 mandatory |
| `static-light` | 学历/家庭出身/子女 且 无应期信号 | 否 | 否 | 学历/家庭: 轻量结构化 + `答案: X`; 子女: 单字母 |
| `other` | 其余题型 | 否 | 可选 | 题型指南 + 可选结构化 |

路由实现在 `contest_channel_route.py`; 结构化推理开关在 `mcq_reasoning_mode.py`.

### 决策 5: 家庭出身子题型 + 规则分 (P0-E, 保留 A+B)

**A 子题型路由** (`family_subtheme.py`):
- `family-death-father` / `family-death-mother`: 丧亲应期, 选项含年份或题干含离世
- `family-wealth-tier`: 贫/富/小康/孤儿层级
- `family-relation`: 父母关系/状况/职业叙事; 贫富与叙事混合时归 relation

**B 规则分提示** (`family_option_scorer.py`):
- 家庭 structured MCQ 注入 `【家庭出身选项规则分】`, 替代通用 `build_year_option_score_block`
- 规则分仅供互证; prompt 明确不得单凭分数作答

**保留基线:** `contest8_sub_jiating_ab2.json` (5/14)。方案 C/D/E 已实验并回退.

### 决策 6: 子女子题型 + 出生年规则分 (P0, 保留)

**子题型** (`children_subtheme.py`): `children-birth-year` / `children-dayun-span` / `children-status`

**规则分** (`children_option_scorer.py`): 男官杀/女食伤, 时支冲合, 育龄/伏吟/日冲校准; 报告 `contest8_sub_zinv_p1.json` (3/5).

**纠偏:** 孩子仅为背景的财运题改判 `职业财运`.

### 决策 7: 婚姻感情 full 通道 (P2, 首轮未达门禁)

- 默认 `votes=3` (仅 full 通道, CLI 未显式提高时)
- 扩展 `MARRIAGE_REASONING_GUIDE` 与 conservative guard
- 基线 12/43; p2 11/43; p3 9/43; p4 8/43; **p5 12/43** (回退 p2 prompt, 子题型仅评测元数据)
- **决策 8 (p5, 保留基线)**: 规则分 top1 准确率 < 60% 时禁止进 prompt; **p5 为婚姻 prompt 最终配置** (votes=3 + `MARRIAGE_REASONING_GUIDE` + `LIUNIAN_REASONING_FORMAT` + 【置信】【目标年】); p6 子题型 format 路由 **11/43** 已回退
- 4.2 婚姻锚点 p4 已试验后 p5 回退; 健康题虚龄锚点仍待做
- 离线保留: `marriage_subtheme.py`, `marriage_option_scorer.py` (top1 约 30%), `build_marriage_option_years_anchor`

### 决策 9: 职业财运子题型 + p2 prompt 基线 (P3, 保留)

**子题型** (`career_subtheme.py`):
- `wealth`: 财运/身家/收入/投资/买房
- `career-status`: 现职/从事行业/职业名称 (无应期年份主导)
- `career-year-event`: 公历年份/虚龄/工作变动/突破
- `major-industry`: 科系取向

**Prompt** (`prompts_contest.py`):
- `get_career_subtheme_guide()` 按子类注入 `CAREER_*_GUIDE` 与对应 reasoning format
- **p2 核心**: `career-status` 使用【选项对照】+ `CAREER_STATUS_MANDATORY_GUIDE`, 禁止七杀/食伤刻板映射 (p1 失败教训)
- wealth/year-event/major 各有专用 format; 应期类 MAY 走 yingqi 并 force 流年块

**主题词**: `contest8_rag.py` 增补 `身家`/`年薪`/`投资`

**评测**: `contest8_eval.py` 输出 `careerSubtheme`; 子集命令 `--themes 职业财运 --tag qishi_p2`

**保留基线:** `contest8_sub_qishi_p2.json` (**18/38 = 47.4%**). p3 (status/year 二次分流 + wealth-tier 格式) 与 p3b **已回退**, 不得作为默认 prompt.

**非目标 (本阶段已确认):** 不做紫微融合、不新增职业规则分块、不改 RAG top_k (5.2 待做).

**曾考虑的替代方案:**
- 仅加长 prompt、不拆分通道: 已证对应期题有害, 否决。
- 每题型独立 LLM 调用: 成本与维护过高, 否决。

### 决策 2: 分阶段提升顺序 (先弱后强)

1. **P0 静态题型** (学历, 家庭出身, 子女) - 学历 6/8、家庭 A+B 5/14、子女 3/5 已完成; 门禁: 静态子集 >= 40% (22 题学历+家庭已 50%).
2. **P1 应期题型** (流年事件, 含年份的综合) - 虚龄锚点、无保守约束; 门禁: 流年事件 >= 50% (19 题)。
3. **P2 婚姻感情 + 健康疾病** - full 通道 votes=3 (已启动); 门禁: 婚姻 >= 35% (43 题, 基线 12/43).
4. **P3 职业财运 + 性格外貌** - 职业子题型 + CAREER_* prompt (p2 基线 18/38); other 通道 RAG top_k=2 待做; 门禁: 职业 >= 14/32, 性格 >= 6/15, 合计 >= 18/47.
5. **P4 长尾** (田宅, 官非, 子女应期) - 针对性流年规则; 门禁: 各 >= 25%, 全量 >= 69。

### 决策 3: 评测门禁

每阶段合并前必须通过:
- 题型子集 JSON 写入 `code/backend/data/reports/contest8_sub_<theme>_<tag>.json`
- `tasks.md` 对应项勾选, PR/提交说明中记录准确率
- P0+P1 完成后 val 40 题 smoke 相对上一阶段 val 不得退步, 再跑全量 200

**常用命令:**
```powershell
cd d:\ZY\code\backend
py -3.10 scripts/run_contest_theme_subset.py --themes 学历 --fewshot --tag xueli --out data/reports/contest8_sub_xueli.json
py -3.10 scripts/run_contest_theme_subset.py --themes 子女 --fewshot --tag zinv_p1 --out data/reports/contest8_sub_zinv_p1.json
py -3.10 scripts/run_contest_theme_subset.py --themes 婚姻感情 --fewshot --tag hunyin_p2 --out data/reports/contest8_sub_hunyin_p2.json
py -3.10 scripts/run_contest_theme_subset.py --themes 职业财运 --fewshot --tag qishi_p2 --out data/reports/contest8_sub_qishi_p2.json
py -3.10 scripts/run_contest_benchmark.py --split val --fewshot --out data/reports/contest8_val_<tag>.json
py -3.10 scripts/run_contest_benchmark.py --split all --fewshot --out data/reports/contest8_<split>_bazi_liunian.json
```

### 决策 4: 按错因标签驱动修复

根据错题 `error_labels` 在题型内选择下一刀:
- `wrong_liunian` / `wrong_dayun` -> 锚点 / 岁运 prompt / luck_chart
- `wrong_yongshen` / `wrong_tiaohou` -> 加强 KG 块, 不用命例 RAG
- `case_overfit` -> 该通道关闭命例 RAG

## 风险与权衡

- **LLM 波动** (尤其婚姻 43 题): full 通道 alone 使用 votes=3 缓解。
- **题型关键词冲突** (如题干含「疾病」): 健康题型强制走 full, 按设计覆盖。
- **评测耗时**: 优先子集; 全量 200 仅在阶段边界跑 (~3 小时/次)。

## 迁移计划

1. 合入路由模块与测试 (已启动)。
2. 按 P0-P4 顺序执行 `tasks.md`; 每个 PR 引用 OpenSpec 任务编号。
3. 全量门禁通过后更新 `report/命理师大赛-全量200题-bazi_liunian.md`。
4. 连续两次全量 >= 69/200 后执行 `openspec archive improve-contest-accuracy-by-theme --yes`。

## 待决问题

- 无明确年份的「综合」题走 static-light 还是 yingqi? **默认 other**, 待实验。
- train 划分是否全程关闭命例 RAG? **推迟到 P2 再定**; val 实验结果不一。
