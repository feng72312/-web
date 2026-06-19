## MODIFIED Requirements

### Requirement: 按题型分流的 MCQ 通道路由

大赛基准评测 MUST 在调用 LLM 之前, 将每道 MCQ 归入且仅归入一种 prompt 通道: `full`、`yingqi`、`static-light` 或 `other`。其中 `static-light` 与 `yingqi` 在学历、家庭出身题型上 MAY 进一步使用题型专用 prompt 变体 (见「静态题型专用 prompt 指南」).

#### Scenario: 婚姻或健康题使用 full 通道

- **WHEN** `infer_question_theme(question)` 为婚姻感情或健康疾病
- **THEN** 系统运行 `BaziJudgementChain`, 启用命例 RAG, 并向 prompt 注入判盘预结论与保守作答约束

#### Scenario: 无应期信号的学历或家庭出身使用 static-light 通道

- **WHEN** 题型为学历或家庭出身, 且 `has_explicit_timing_signal(question, options)` 为 false
- **THEN** 系统跳过判盘链与命例 RAG, 不注入完整流年时间轴块, 启用该题型轻量结构化推理格式, 并要求最后一行输出 `答案:` + 单字母

#### Scenario: 无应期信号的子女题使用 static-light 通道

- **WHEN** 题型为子女, 且 `has_explicit_timing_signal(question, options)` 为 false
- **THEN** 系统跳过判盘链与命例 RAG, 关闭结构化 elimination 推理, 不 force 完整流年块, 要求模型输出单字母 MCQ 答案

#### Scenario: 应期题使用 yingqi 通道

- **WHEN** 题型不是婚姻感情/健康疾病, 且 (`has_explicit_timing_signal(question, options)` 为 true 或题型为流年事件), 且不属于「学历/家庭出身 + 选项含年份」的题型专用 yingqi 变体所单独覆盖的路径
- **THEN** 系统跳过全量判盘链与命例 RAG, 注入虚龄/大运锚点与通用应期推理格式, 且不施加保守约束

#### Scenario: 学历选项含年份时使用学历应期变体

- **WHEN** 题型为学历, 且 `has_explicit_timing_signal(question, options)` 为 true (含选项内多个公历年份)
- **THEN** 系统走 yingqi 通道, 使用学历应期 mandatory 与「选项年份」推理格式, 并 MAY 注入选项年份岁运评分块

#### Scenario: 家庭出身选项含年份时使用家庭应期变体

- **WHEN** 题型为家庭出身, 且 `has_explicit_timing_signal(question, options)` 为 true
- **THEN** 系统走 yingqi 通道, 使用家庭应期 mandatory 与「选项年份 + 父母星」推理格式, 并 MAY 注入家庭出身选项规则分块

### Requirement: 题型子集评测

后端 MUST 提供脚本或命令行参数, 在不修改数据集文件的前提下, 按题型列表和/或 question_id 列表过滤 Contest8 MCQ 并评测。

#### Scenario: 运行单一题型子集

- **WHEN** 操作者指定题型列表 (如 `学历,家庭出身`) 运行子集评测
- **THEN** 系统仅评测匹配题型的题目, 并输出含 `correct`/`total`/`accuracy` 与 `questionIds` 的 JSON

#### Scenario: 按 question_id 过滤子集

- **WHEN** 操作者指定 `--ids P018-Q6,P027-Q11` 等逗号分隔 ID
- **THEN** 系统仅评测数据集中存在的对应题目 (仍可与 `--themes` 组合过滤)

## ADDED Requirements

### Requirement: 静态题型专用 prompt 指南

系统 MUST 为 static-light 下的学历与家庭出身注入题型专用推理指南, 且不得使用 marriage/health full 通道的保守约束。

#### Scenario: 静态学历 prompt

- **WHEN** 学历题处于 static-light 通道
- **THEN** prompt 包含学历层级断法 (印星/财坏印/早运大运/同层级比较), 并使用「印星学业 + 层级排除」轻量格式, 而非完整「目标年 + 流年时间轴」模板

#### Scenario: 静态家庭出身 prompt

- **WHEN** 家庭出身题处于 static-light 通道
- **THEN** prompt 包含父母星与年月柱断法 (偏财为父、印为母、贫富贵判断), 并使用「父母家运 + 选项排除」轻量格式

### Requirement: 家庭出身子题型路由

`infer_question_theme == 家庭出身` 时, 系统 MUST 进一步路由至子题型, 并注入对应专用推理指南.

#### Scenario: 丧父应期子类

- **WHEN** 题干或选项表明父亲去世/丧父, 且选项含年份
- **THEN** 子类为 `family-death-father`, prompt 使用丧父专用指南

#### Scenario: 丧母应期子类

- **WHEN** 题干或选项表明母亲离世/丧母, 且选项含年份
- **THEN** 子类为 `family-death-mother`, prompt 使用丧母专用指南

#### Scenario: 贫富层级子类

- **WHEN** 题干或选项主要为贫/富/小康/孤儿层级
- **THEN** 子类为 `family-wealth-tier`, prompt 使用贫富层级专用指南

#### Scenario: 家庭关系叙事子类

- **WHEN** 题干问父母关系/状况, 或选项含职业叙事与贫富混合
- **THEN** 子类为 `family-relation`, prompt 使用关系叙事专用指南

### Requirement: 家庭出身选项规则分

家庭出身 structured MCQ 在启用 elimination 推理时 MUST 尝试注入 `【家庭出身选项规则分】` 提示块; 规则分仅供与排盘互证, 不得作为唯一作答依据。

#### Scenario: 家庭出身题优先规则分块

- **WHEN** 题型为家庭出身且启用 structured MCQ
- **THEN** 系统使用 `build_family_option_score_block` 替代通用岁运评分块

#### Scenario: 规则分不得强制选最高分

- **WHEN** 规则分块注入 prompt
- **THEN** 块内 MUST 说明不得单凭分数作答或排除冲根/合去之年

### Requirement: 题型关键词纠偏

`infer_question_theme` MUST 在通用关键词匹配前处理已知冲突, 避免题干同时含「毕业/大学」与职业取向词时被误判为学历。

#### Scenario: 毕业后行业归职业财运

- **WHEN** 题干含「行业」「从事」「科系」或「现职」之一
- **THEN** `infer_question_theme` 返回 `职业财运`, 即使题干同时含「毕业」或「大学」

### Requirement: 选项年份识别

应期信号检测 MUST 将 MCQ 选项内、中文或英文逗号后的公历年份计入选项年份型 MCQ。

#### Scenario: 中文逗号前缀年份

- **WHEN** 某选项文本含 `，2004年` 或 `,2004年` 等形式
- **THEN** `is_year_option_mcq(options)` 将该选项计为含年份选项; 当含年份选项数 >= 2 时 `has_explicit_timing_signal` 为 true
