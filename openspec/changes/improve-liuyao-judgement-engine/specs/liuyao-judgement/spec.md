## ADDED Requirements

### Requirement: 六爻典籍 source manifest

系统 MUST 为 `数据库/02六爻卜筮` 下每个资料文件维护机器可读的 manifest 条目, 包含 `authorityTier`, `libraryRole`, `evidenceRole`, `classic`, `canJudge`, `judgmentPolicy`, `domains`, `topicScope`, `readStatus`。

#### Scenario: S 级主裁经典可进入主裁检索

- **WHEN** manifest 中文件位于 `S_主裁经典/` 且 `canJudge=true`
- **THEN** 该文件 chunk 可进入 `primaryEvidence` 检索范围, 且 `judgmentPolicy` 为 `can_primary_judge`

#### Scenario: B 级现代技法不得主裁

- **WHEN** manifest 中文件位于 `B_现代技法/` 且 `canJudge=false`
- **THEN** 该文件 chunk 仅可进入 `modernSupport` 分区, `judgmentPolicy` 为 `explain_only`

### Requirement: 六爻 RAG chunk 权威分层

重建 `kb_02_liuyao` 时, 每个 chunk MUST 携带 `authorityTier`, `libraryRole`, `evidenceRole`, `classic`, `textRole`, `topicScope`, `caseOnly` metadata, 且索引路径反映 `S_主裁经典/`、`A_辅助经典/`、`B_现代技法/` 目录结构。

#### Scenario: 用神规则检索优先 S 级

- **WHEN** 裁判链触发 `topic=yong_shen` 节点并请求 RAG 证据
- **THEN** 返回结果中 S 级《增删卜易》或《卜筮正宗》片段排在 B 级曲炜讲义之前

#### Scenario: 卦例片段降权

- **WHEN** chunk `caseOnly=true`
- **THEN** 该 chunk 仅可进入 `caseReference` 分区, 不得作为 `primaryEvidence` 唯一依据

#### Scenario: P0 索引重建验收

- **WHEN** 操作者运行 `classify_02_sources.py` 与 `build_index.py --no-reset --category 02六爻卜筮`
- **THEN** `liuyao_sources_manifest.json` 含 16 文件, `kb_02_liuyao` 报告 5306 chunks, 且 `spot_check_liuyao_metadata.py` 返回 `sTierFirstInOpenSearch=true`

### Requirement: 六爻 manifest 校验脚本

系统 MUST 提供 `classify_02_sources.py` 生成 manifest, 并支持 `--validate-only` 校验磁盘文件与 manifest 条目一致。

#### Scenario: manifest 与资料目录一致

- **WHEN** 操作者运行 `py -3.10 classify_02_sources.py --validate-only`
- **THEN** 脚本退出码为 0, 且 16 个 S/A/B 资料文件均能在 manifest 中找到

### Requirement: 六爻资料解密前置 (decrypt skill)

在 manifest 生成、RAG 索引重建、规则节点抽取之前, 若 `数据库/02六爻卜筮` 下资料疑似被公司加密软件锁定 (只读、乱码、索引 `empty`/`error`), 操作者 MUST 先使用 decrypt skill 的全局脚本解密, 不得跳过或模拟解密。

解密脚本路径固定为:

`C:\Users\liqingfeng\.cursor\skills\decrypt\scripts\file_decrypt.py`

(或项目内等价的 `d:\ZY\file_decrypt.py`, 行为须一致)

#### Scenario: 整理目录前批量解密

- **WHEN** 操作者运行 `py -3.10 classify_02_sources.py --decrypt` 且目标目录为 `数据库/02六爻卜筮`
- **THEN** 系统先调用 `file_decrypt.py` 递归解密该目录, 输出 success/failed/skipped 统计, 再扫描生成 manifest

#### Scenario: 索引前发现加密导致读取失败

- **WHEN** `build_index.py` 对某六爻资料返回 `empty` 或 `error`, 且文件在资源管理器中为只读或内容乱码
- **THEN** 操作者先对 `数据库/02六爻卜筮` 执行 decrypt skill 解密, 再重跑 `build_index.py --no-reset --category 02六爻卜筮`, 不得将加密文件计入 `ok` 状态

#### Scenario: 解密失败不破坏原文件

- **WHEN** `file_decrypt.py` 对某文件返回 `[FAIL]`
- **THEN** 该文件保持原状, manifest 标记 `readStatus=encrypted_or_unreadable`, 不进入主裁检索与规则抽取, 并记录于整理报告

### Requirement: 六爻占事分类裁判

`LiuyaoJudgementChain` MUST 在旺衰与吉凶判断之前, 将用户问事归入占事主题 (如求财、求官、婚姻、疾病、出行等), 并输出 `topicId`, `topicLabel`, `candidateYongShen`, `confidence`。

#### Scenario: 求财问事归类

- **WHEN** 问事含求财、生意、收入等语义
- **THEN** `TopicJudge` 输出 `topicId=wealth`, `candidateYongShen=妻财`

#### Scenario: 自占疾病归类

- **WHEN** 问事为自占疾病或健康
- **THEN** `TopicJudge` 输出 `topicId=self_illness`, 候选用神包含世爻与官鬼规则路径

### Requirement: 六爻用神规则裁判

用神判定 MUST 优先使用规则裁判 (`YongShenJudge`), 结合占事分类、卦中六亲分布与伏神规则定位爻位; AI 推断仅作 fallback, 且输出 `source` 字段区分 `rule` 与 `ai`。

#### Scenario: 问官取官鬼爻

- **WHEN** 占事分类为求官, 且卦中存在官鬼六亲爻
- **THEN** `YongShenJudge` 取官鬼为用神并返回其爻位, `source=rule`

#### Scenario: 用户覆盖用神保留审计

- **WHEN** 用户通过 `YongShenEditor` 手动覆盖用神
- **THEN** 系统接受覆盖并在 judgement 输出中记录 `override=true` 与覆盖原因

#### Scenario: 规则用神优先于 AI

- **WHEN** `TopicJudge` 置信度 >= 0.45 且卦中存在候选用神六亲
- **THEN** `YongShenService` 返回 `source=rule` 与 `confidence`, 不调用 AI 推断

### Requirement: 六爻规则图谱节点

`liuyao_nodes.jsonl` MUST 包含不少于 55 条可执行规则节点 (占事/用神/旺衰/动变/应期等), 并保留 64 卦名节点; 节点 MUST 含 `domain=liuyao`, `topic`, `classic`, `lookupKey`。

#### Scenario: 规则节点规模达标

- **WHEN** 操作者运行 `append_liuyao_rule_nodes.py`
- **THEN** 输出 `ruleNodes >= 55` 且写入 `code/knowledge/data/graph/liuyao_nodes.jsonl`

### Requirement: 六爻旺衰生克与世应动变裁判

判盘链 MUST 包含旺衰生克裁判 (月建、日辰、旬空、月破、原神忌神仇神、动变生克) 与世应动变裁判 (世应关系、动爻、变卦、六冲、反吟伏吟), 并输出结构化结论与置信度。

#### Scenario: 用神月破降置信

- **WHEN** 用神爻值月破
- **THEN** `WangShuaiJudge` 标记 `yuePo=true`, 仲裁结论降低置信度并提示需看填实或生扶

#### Scenario: 近病逢六冲专题规则

- **WHEN** 占事分类为近病, 且本卦或变卦为六冲
- **THEN** `DongBianJudge` 触发六冲专题节点, 结论边界区分近病与久病, 不得一律断凶

### Requirement: 六爻判盘链仲裁与分层证据

系统 MUST 通过 `LiuyaoArbiter` 合并各裁判意见, 输出冲突说明与最终置信边界; RAG 证据 MUST 分区为 `primaryEvidence`, `secondaryEvidence`, `caseReference`, `modernSupport`, `excludedOrLowTrust`。

#### Scenario: 用神旺但忌神发动

- **WHEN** 用神得月建生扶, 且忌神爻发动克用神
- **THEN** 仲裁结论为「有基础但受阻」, 非简单大吉或大凶, 且 `conflicts` 数组含双方裁判摘要

#### Scenario: 缺少主裁证据

- **WHEN** 某结论无 S/A 级主裁片段支持
- **THEN** 系统降低置信度, 并在报告中提示「缺少主裁证据」, 不以 B 级讲义补位假装权威

### Requirement: 六爻 judgement API

后端 MUST 提供 `POST /api/v1/liuyao/judgement`, 接受 `chart`, `question`, 可选 `yongShen`, 返回完整裁判链、`tieredEvidence` 与 `confidence`; 现有 `/interpret` MUST 保持可用且可内部复用 judgement 结果。

#### Scenario: 调用 judgement 获取裁判链

- **WHEN** 客户端提交合法卦象与问事
- **THEN** 响应包含 `judgement.judges[]` (各裁判名称、结论、置信度) 与 `tieredEvidence` 五分区

#### Scenario: interpret 向后兼容

- **WHEN** 客户端仅调用现有 `/interpret` 端点
- **THEN** 响应仍包含 `summary` 与 `excerpts`, 且 AI 提示词约束为仅根据 judgement 与证据链表达

#### Scenario: P2 判盘链 smoke 验收

- **WHEN** 操作者运行 `py -3.10 scripts/smoke_judgement_liuyao_local.py`
- **THEN** 输出 `stepCount >= 8`, `judgeCount >= 8`, 含旺衰 `wangShuaiFlags` 与动变 `dongBianSummary`, 退出码为 0

#### Scenario: 卦象增强字段写入 enrichedChart

- **WHEN** `LiuyaoJudgementChain` 处理合法卦象
- **THEN** `enrichedChart.lines[]` 含 `kongPoState`, `lineStrength`, `dongBianTarget`, 且顶层 `riskFlags` 标记六冲与动爻数

### Requirement: 六爻 AI 表达约束

六爻解读 prompt MUST 要求: 不得编造爻位与六亲, 不得把卦例当规则, 不得用 B 级现代讲义推翻 S/A 主裁证据, 不得在用神未判定时直接断吉凶; 证据不足时必须明确说明。

#### Scenario: 专业版与白话版同一判断链

- **WHEN** 用户请求 `style=professional` 或 `style=plain`
- **THEN** 两者引用同一套 `LiuyaoJudgementChain` 结论, 仅表达方式不同

### Requirement: 六爻前端判盘报告

前端 MUST 在六爻 Tab 展示判盘报告: 起卦规则、月建日辰、用神、卦象高亮 (用神/世应/动爻/空破), 裁判意见分区与分层典籍证据。

#### Scenario: 展示分层证据

- **WHEN** judgement API 返回 `tieredEvidence`
- **THEN** UI 以「主裁典籍」「辅助古籍」「卦例参考」「现代补充」分区展示, 样式可区分权限

#### Scenario: interpret 返回 tieredEvidence 五分区

- **WHEN** 客户端调用 `/interpret` 且 RAG 可用
- **THEN** `interpretation.tieredEvidence` 含 `primaryEvidence`, `secondaryEvidence`, `caseReference`, `modernSupport`, `excludedOrLowTrust` 五类字段 (可为空数组)

#### Scenario: 卦象高亮用神世应空破

- **WHEN** 前端获得 `judgement.enrichedChart` 与用神爻位
- **THEN** `HexagramBoard` 高亮用神行, 并标记世应、动爻、旬空、月破

#### Scenario: P3 前端判盘面板验收

- **WHEN** 用户完成起卦且后端 `/judgement` 可用
- **THEN** `LiuyaoTab` 展示 `LiuyaoJudgementPanel`, 含占事/用神/裁判步骤/分层典籍五区

#### Scenario: P3 API smoke 验收

- **WHEN** 操作者运行 `py -3.10 scripts/smoke_judgement_liuyao_api.py --base http://127.0.0.1:8000`
- **THEN** 响应 `judgeCount >= 8`, `enrichedLineCount >= 6`, `hasKongPoState=true`, 退出码为 0

#### Scenario: P3 tiered evidence 分区单测

- **WHEN** 操作者运行 `py -3.10 -m pytest tests/test_liuyao_tiered_evidence.py`
- **THEN** S/A/B/caseOnly 片段分别落入 primary/secondary/modern/case 桶, 退出码为 0

### Requirement: 六爻评测回归门禁

后端 MUST 提供六爻回归脚本 `run_liuyao_regression_gate.py`, 支持 liuyao-only contest 评测, 输出 `liuyaoPred`, 准确率与 `errorLabels`; 评测题库 MUST 与生产 RAG 索引隔离。

门禁分两层:

1. **离线层 (无 LLM)**: `LiuyaoJudgementChain` 对 contest 样本起卦, 校验裁判链覆盖率与 enriched 字段
2. **闭卷层 (可选 LLM)**: `predict_one_liuyao_only` 产出非空 `liuyaoPred`, 错因标签可聚类

#### Scenario: liuyao-only smoke 产生预测

- **WHEN** 操作者运行 `run_liuyao_regression_gate.py --smoke` (>= 5 题, val split)
- **THEN** 输出 JSON 中每题 `liuyaoPred` 为非空字母, 且含 `errorLabels` 字段

#### Scenario: 离线裁判链覆盖率门禁

- **WHEN** 操作者运行 `run_liuyao_regression_gate.py --offline-only --limit 10`
- **THEN** 每题 `judgement.judges.length >= 8`, `enrichedChart.lines[].kongPoState` 存在, 报告 `coverageRate >= 0.95`

#### Scenario: 错因标签驱动修复

- **WHEN** 评测结果含 `wrong_yong_shen` 或 `ignore_kong_po` 标签
- **THEN** 报告 `errorLabelCounts` 按标签聚类计数, 供下一阶段规则补全优先级排序

#### Scenario: judgement 注入 contest 提示词

- **WHEN** `predict_one_liuyao_only` 启用 `use_judgement=true`
- **THEN** MCQ prompt 含裁判链摘要与分层证据预览, 用神优先取自 `YongShenJudge` 规则结果

#### Scenario: 评测与生产 RAG 隔离

- **WHEN** RAG 检索生产索引 `kb_02_liuyao`
- **THEN** contest 题库文件不得出现在索引 manifest 与 chunk metadata 中

### Requirement: 六爻错因标签模块

系统 MUST 提供 `code/backend/app/benchmark/liuyao_error_labels.py`, 对 contest 六爻错题推断 `errorLabels`, 并支持 `aggregate_error_label_counts` 聚类输出。

标签集 MUST 至少包含: `wrong_topic_class`, `wrong_yong_shen`, `ignore_yue_jian`, `ignore_kong_po`, `wrong_dong_bian`, `case_overfit`, `modern_notes_override`, `overconfident_claim`, `empty_prediction`。

#### Scenario: 答错时推断用神标签

- **WHEN** `predict_one_liuyao_only` 返回 `liuyaoPred` 与 `gold` 不一致, 且 `judgement.yongShen.source=ai`
- **THEN** `errorLabels` 含 `wrong_yong_shen`

#### Scenario: 预测为空时标记管道故障

- **WHEN** `liuyaoPred` 为空字符串
- **THEN** `errorLabels` 含 `empty_prediction`

### Requirement: P0-P4 变更整体验收

本变更全部阶段 (P0-P4) 完成后, 操作者 MUST 能通过下列门禁脚本复现验收结果; 准确率 baseline 仅记录, 不作首次发布硬门禁。

#### Scenario: P4 回归门禁通过

- **WHEN** 操作者运行 `py -3.10 scripts/run_liuyao_regression_gate.py --smoke --limit 5`
- **THEN** `liuyao_regression_gate.json` 中 `passed=true`, `offlineCoverage.coverageRate >= 0.95`, `smokeContest.nonemptyPred=5`

#### Scenario: P4 contest smoke 基线记录

- **WHEN** 操作者查看 `report/六爻卜筮最强方案/contest8_liuyao_smoke.json`
- **THEN** 报告记录 val 子集准确率与每题 `liuyaoPred`, `errorLabels`, `judgement` 字段

#### Scenario: 全量六爻单测通过

- **WHEN** 操作者运行 `py -3.10 -m pytest tests/test_liuyao_*.py -q` (topic/yong_shen/judgement/tiered/error_labels/predict 等)
- **THEN** 30 项测试通过, 退出码为 0

#### Scenario: OpenSpec 严格校验

- **WHEN** 操作者运行 `openspec validate improve-liuyao-judgement-engine --strict`
- **THEN** 退出码为 0
