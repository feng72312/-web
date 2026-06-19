## ADDED Requirements

### Requirement: 紫微典籍 source manifest

系统 MUST 为 `数据库/11紫微斗数` 下每个资料文件维护机器可读的 manifest 条目, 包含 `authorityTier`, `libraryRole`, `evidenceRole`, `school`, `topicScope`, `canJudge`, `canOverride`, `judgmentPolicy`, `readStatus`, `sourceType`。

#### Scenario: S 级核心法本可进入主裁检索

- **WHEN** manifest 中文件位于 `S_核心法本/` 且 `canJudge=true`
- **THEN** 该文件 chunk 可进入 `primaryEvidence` 检索范围, 且 `judgmentPolicy` 为 `can_primary_judge_after_chunk_tag` 或等价主裁策略

#### Scenario: B 级技法补充不得主裁

- **WHEN** manifest 中文件位于 `B_技法补充/` 且 `canJudge=false`
- **THEN** 该文件 chunk 仅可进入 `secondaryEvidence` 或现代解释分区, `judgmentPolicy` 为 `explain_only`

#### Scenario: C 级宫位专题仅主题辅助

- **WHEN** manifest 中文件位于 `C_宫位专题/` 且 `libraryRole=topic_library`
- **THEN** 该文件 chunk 仅在对应 `palaceScope` 主题查询中作为辅助, 不得泛化为全盘主裁

### Requirement: 紫微 RAG chunk 权威分层

重建 `kb_11_ziwei` 时, 每个 chunk MUST 携带 `authorityTier`, `libraryRole`, `evidenceRole`, `school`, `textRole`, `topicScope`, `palaceScope`, `starScope`, `mutagenScope`, `limitScope` metadata, 且索引路径反映 `S_核心法本/`、`A_系统教材/`、`A_星曜格局/`、`B_技法补充/`、`C_宫位专题/` 目录结构。

#### Scenario: 星曜规则检索优先 S 级

- **WHEN** 裁判链触发 `topic=star` 节点并请求 RAG 证据
- **THEN** 返回结果中 S 级《太微赋》或全书体系片段排在 B 级现代讲义之前

#### Scenario: 命例片段降权

- **WHEN** chunk `textRole=case`
- **THEN** 该 chunk 仅可进入 `caseReference` 分区, 不得作为 `primaryEvidence` 唯一依据

#### Scenario: P0 索引重建验收

- **WHEN** 操作者运行 `classify_11_sources.py` 与 `build_index.py --no-reset --category 11紫微斗数`
- **THEN** `ziwei_sources_manifest.json` 含规划内全部可读文件, `kb_11_ziwei` 报告中 `cannot read doc` 失败数为 0, 且 `spot_check_ziwei_metadata.py` 返回 S 级优先于 B 级

### Requirement: 紫微 manifest 校验脚本

系统 MUST 提供 `classify_11_sources.py` 生成 manifest, 并支持 `--validate-only` 校验磁盘文件与 manifest 条目一致。

#### Scenario: manifest 与资料目录一致

- **WHEN** 操作者运行 `py -3.10 classify_11_sources.py --validate-only`
- **THEN** 脚本退出码为 0, 且 S/A/B/C 规划内资料文件均能在 manifest 中找到

### Requirement: 紫微资料解密前置 (decrypt skill)

在 manifest 生成、RAG 索引重建、规则节点抽取之前, 若 `数据库/11紫微斗数` 下资料疑似被公司加密软件锁定 (只读、乱码、索引 `empty`/`error`), 操作者 MUST 先使用 decrypt skill 的全局脚本解密, 不得跳过或模拟解密。

解密脚本路径固定为:

`C:\Users\liqingfeng\.cursor\skills\decrypt\scripts\file_decrypt.py`

(或项目内等价的 `d:\ZY\file_decrypt.py`, 行为须一致)

#### Scenario: 整理目录前批量解密

- **WHEN** 操作者运行 `py -3.10 classify_11_sources.py --decrypt` 且目标目录为 `数据库/11紫微斗数`
- **THEN** 系统先调用 `file_decrypt.py` 递归解密该目录, 输出 success/failed/skipped 统计, 再扫描生成 manifest

#### Scenario: 索引前发现加密导致读取失败

- **WHEN** `build_index.py` 对某紫微资料返回 `empty` 或 `error`, 且文件在资源管理器中为只读或内容乱码
- **THEN** 操作者先对 `数据库/11紫微斗数` 执行 decrypt skill 解密, 再重跑 `build_index.py --no-reset --category 11紫微斗数`, 不得将加密文件计入 `ok` 状态

#### Scenario: 解密失败不破坏原文件

- **WHEN** `file_decrypt.py` 对某文件返回 `[FAIL]`
- **THEN** 该文件保持原状, manifest 标记 `readStatus=encrypted_or_unreadable`, 不进入主裁检索与规则抽取, 并记录于整理报告

#### Scenario: doc 格式无法读取时转换后重试

- **WHEN** 索引报告对 `.doc` 返回 `cannot read doc file` 且解密后仍无法读取
- **THEN** 操作者将文件转为 `.docx` 或 `.txt`, 更新 manifest 路径映射, 再重建索引, 不得将未转换文件标为 `ok`

### Requirement: 紫微排盘法库可审查

每次排盘结果 MUST 在结构化输出中包含 `rulesMeta`, 说明闰月规则、早晚子时、真太阳时、四化表、法派选择; 规则变更导致命宫或四化变化时 MUST 返回可审查警告。

#### Scenario: chart 响应含排盘规则

- **WHEN** 客户端调用 `POST /api/v1/ziwei/chart` 且传入 `rules`
- **THEN** 响应 `chart.rulesMeta` 含上述规则字段及来源说明

#### Scenario: 规则切换提示差异

- **WHEN** 同一命盘在两种四化表下命宫或关键四化落点不同
- **THEN** 系统输出 `ruleChangeWarning`, 说明「规则差异会改变判断」

### Requirement: 紫微本命盘结构化增强

`normalize_chart` 或等价 enrich 步骤 MUST 为每宫输出 `palaceStrength`, `triadEvidence`, `oppositeEvidence`, 空宫借对宫主星标注, 以及 `mutagenState`, `riskFlags` 等中间指标供裁判器使用。

#### Scenario: 空宫借对宫显式标注

- **WHEN** 某宫无主星且对宫有主星
- **THEN** enrich 输出 `borrowedFromOpposite=true` 及借星名称, 不得仅标记「无主星」

#### Scenario: 三方四正证据可追踪

- **WHEN** 裁判器查询命宫主题
- **THEN** enrich 输出包含命宫、财帛、官禄、迁移三方四正星曜与庙旺摘要

### Requirement: 紫微宫位裁判

`ZiweiJudgementChain` MUST 包含 `PalaceJudge`, 每个宫位仅在其主题边界内给结论, 且结合三方四正与对宫, 不得单宫越权断全局。

#### Scenario: 夫妻宫裁判不替代命宫格局

- **WHEN** 问事主题为婚恋且夫妻宫化忌
- **THEN** `PalaceJudge` 在夫妻主题给出风险结论, 命宫格局结论独立保留, 仲裁器合并为分区判断

#### Scenario: 官禄判断含三方四正

- **WHEN** 占事涉及事业
- **THEN** 官禄裁判结论引用官禄、命宫、财帛、迁移及四化引动, 非仅读本宫主星

### Requirement: 紫微星曜与四化裁判

判盘链 MUST 包含 `StarJudge` 与 `MutagenJudge`; 星曜结论须结合落宫、庙旺、同宫组合、三方四正、辅煞与限运; 四化裁判 MUST 输出方向性 (来源宫、落宫、冲照宫、scope)。

#### Scenario: 四化飞忌方向完整

- **WHEN** 飞星派下夫妻宫宫干化忌入命宫
- **THEN** `MutagenJudge` 输出 `fromPalace=夫妻`, `toPalace=命宫`, `mutagenType=忌`, `scope=natal|decadal|yearly`

#### Scenario: 单星口诀不得全盘定论

- **WHEN** 仅贪狼落夫妻且无其他格局/四化支撑
- **THEN** 裁判链不得输出「全盘桃花旺」类结论, 置信度受限于单宫证据

### Requirement: 紫微格局裁判

`PatternJudge` MUST 对可结构化格局 (如杀破狼、府相朝垣、机月同梁、日月并明/反背等) 校验成立条件、破格条件、救应条件与四化修正, 不得仅凭单星名称命中。

#### Scenario: 杀破狼需三星位置校验

- **WHEN** 盘中仅见破军而无七杀贪狼于命迁财官相关位置
- **THEN** `PatternJudge` 不触发杀破狼格局节点

### Requirement: 紫微限运裁判

`LimitJudge` MUST 分层处理本命、大限、流年、小限, 判断大限命宫落宫、冲照本命关键宫、流年引动与事件主题宫位, 并输出时间范围与置信边界。

#### Scenario: 流年引动夫妻宫

- **WHEN** 目标年流年夫妻宫四化冲本命命宫
- **THEN** `LimitJudge` 输出限运事件链含 `trigger=流年`, `theme=婚恋`, `confidence` 边界

### Requirement: 紫微规则图谱节点

`ziwei_nodes.jsonl` MUST 包含不少于 100 条可执行规则节点 (宫位/星曜/四化/格局/限运等), 节点 MUST 含 `domain=ziwei`, `school`, `topic`, `lookupKey`, `conditions`。

#### Scenario: 规则节点规模达标

- **WHEN** 操作者完成 P2 规则抽取批次
- **THEN** `ziwei_nodes.jsonl` 中 `safeAutoAnswer=false` 的可触发节点 >= 100

### Requirement: 紫微判盘链仲裁与分层证据

系统 MUST 通过 `ZiweiArbiter` 合并各裁判意见, 输出冲突说明与最终置信边界; 三合/飞星法派冲突时按用户选择法派主裁; RAG 证据 MUST 分区为 `primaryEvidence`, `secondaryEvidence`, `schoolCommentary`, `caseReference`, `excludedOrUnreadable`。

#### Scenario: 命宫高格与夫妻化忌并存

- **WHEN** 命宫格局佳但夫妻宫化忌
- **THEN** 仲裁结论为「人格与事业承载力强, 婚恋主题有独立风险」, `conflicts` 含双方裁判摘要

#### Scenario: 缺少主裁证据

- **WHEN** 某结论无 S/A 级主裁片段支持
- **THEN** 系统降低置信度, 提示「缺少主裁证据」, 不以 B/C 级讲义补位假装权威

### Requirement: 紫微 judgement API

后端 MUST 提供 `POST /api/v1/ziwei/judgement`, 接受命盘数据与可选 `question`, `targetYear`, `school`, 返回完整裁判链、`tieredEvidence`, `rulesMeta` 与 `confidence`; 现有 `/interpret` MUST 保持可用且可内部复用 judgement 结果。

#### Scenario: 调用 judgement 获取裁判链

- **WHEN** 客户端提交合法紫微命盘与问事
- **THEN** 响应包含 `judgement.judges[]` (各裁判名称、结论、置信度) 与 `tieredEvidence` 五分区

#### Scenario: interpret 向后兼容

- **WHEN** 客户端仅调用现有 `/interpret` 端点
- **THEN** 响应仍包含 `summary` 与 `excerpts`, 且 AI 提示词约束为仅根据 judgement 与证据链表达

#### Scenario: P2 判盘链 smoke 验收

- **WHEN** 操作者运行 `py -3.10 scripts/smoke_judgement_ziwei_local.py`
- **THEN** 输出含宫位/星曜/四化/格局裁判步骤, `judgeCount >= 6`, 退出码为 0

### Requirement: 紫微 AI 表达约束

紫微解读 prompt MUST 要求: 不得编造星曜位置, 不得把单星口诀当全盘结论, 不得把命例当规则, 不得混用未声明法派, 不得用低信材料推翻主裁证据; 证据不足时必须明确说明。

#### Scenario: 专业版与白话版同一判断链

- **WHEN** 用户请求 `style=professional` 或 `style=plain`
- **THEN** 两者引用同一套 `ZiweiJudgementChain` 结论, 仅表达方式不同

### Requirement: 紫微前端判盘报告

前端 MUST 在紫微 Tab 展示判盘报告: 排盘规则、命宫身宫、当前大限流年、十二宫盘面 (三方四正高亮、四化飞线、限运引动), 裁判意见分区与分层典籍证据。

#### Scenario: 展示分层证据

- **WHEN** judgement API 返回 `tieredEvidence`
- **THEN** UI 以「主裁典籍」「辅助古籍」「派别视角」「命例参考」「不可用资料」分区展示, 样式可区分权限

#### Scenario: 盘面高亮三方四正与四化飞线

- **WHEN** 前端获得 `judgement.enrichedChart` 与四化飞星数据
- **THEN** 盘面组件高亮三方四正宫位, 并绘制宫干飞化方向线

### Requirement: 紫微评测回归门禁

后端 MUST 提供紫微回归脚本, 支持 ziwei-only contest 评测, 输出预测、准确率与 `errorLabels`; 评测题库 MUST 与生产 RAG 索引隔离; 支持接入 bazi+ziwei 双轨仲裁权重策略。

#### Scenario: ziwei-only smoke 产生预测

- **WHEN** 操作者运行 `run_ziwei_regression_gate.py` smoke 模式 (>= 5 题)
- **THEN** 输出 JSON 中每题预测为非空选项, 且含 `errorLabels` 字段

#### Scenario: 错因标签驱动修复

- **WHEN** 评测结果含 `wrong_mutagen_direction` 或 `ignore_triad` 标签
- **THEN** 报告按标签聚类计数, 供下一阶段规则补全优先级排序

#### Scenario: 双轨仲裁仅提升适用题型权重

- **WHEN** 题目标注 `ziwei_suitable=true`
- **THEN** bazi+ziwei 合并预测中紫微通道权重高于非适用题, 且记录仲裁来源
