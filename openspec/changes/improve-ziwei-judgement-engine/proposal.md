# 变更: 紫微斗数 Classic-Grounded 判盘引擎升级

## 背景与动机

紫微斗数模块当前已具备 `ZiweiEngine` 排盘 (`iztro-py`)、`ziwei_router` 多接口 (`/rules`, `/chart`, `/rag/search`, `/interpret`, `/chat/init`)、前端 `ZiweiTab` 专业盘与流年大限导航, 但断盘仍停留在「排盘 + 向量检索 + AI 自由发挥」阶段。

`数据库/11紫微斗数` 已完成首轮分类规划 (S 3 / A 7 / B 4 / C 11 / D 2, 共 27 条记录), 历史 RAG 索引 `kb_11_ziwei` 为 25 文件 / 4910 chunk, 但工作区原文目录当前仅保留 2 份 S 级 `.txt` 与分类清单, 25 个 `.doc` 原文需恢复; 索引报告中 12 个 `.doc` 曾出现 `cannot read doc file`, 证据库不完整。

知识图谱 `ziwei_nodes.jsonl` 仅有 26 个泛化节点 (十二宫 + 十四主星), 全部 `safeAutoAnswer=false`, 尚无四化、格局、限运、法派冲突等可执行裁判节点。大赛评测 `contest8_ziwei_only` 已存在: val 15/40 = 37.5%, train 31.7%, test 30.0%; bazi+ziwei 仲裁 val 最好 40.0%, 说明紫微通道能贡献信号, 但尚未稳定压过八字主链。

依据 `report/紫薇斗数最强方案/紫微斗数判盘引擎最强方案.md`, 需要将紫微升级为「排盘法派可控、宫星四化可追溯、限运推理可审查、AI 只负责表达」的专业斗数判盘系统, 并与八字 `BaziJudgementChain`、六爻 `LiuyaoJudgementChain` 形成可互证的多术架构。

## 变更内容

- 建立紫微 **四库分离**: 排盘法库、经典裁判库 (`judge_library` 10)、技法辅助库 (`support_library` 4)、宫位专题库 (`topic_library` 11)、评测基准库 (与生产 RAG 隔离)。
- 恢复并核对 `数据库/11紫微斗数` 原文资料, 接入 **decrypt skill** 前置流程, 防止公司加密或只读锁定导致 manifest/索引/规则抽取失败。
- 生成 `ziwei_sources_manifest.json`, 固化 S/A/B/C/D 分层与 `canJudge` / `judgmentPolicy` / `school` 策略。
- 将 12 个读取失败的 `.doc` 转为 `.docx` 或 `.txt`, 重建 `kb_11_ziwei` 索引, chunk metadata 写入 `authorityTier`, `textRole`, `school`, `palaceScope`, `starScope`, `mutagenScope`, `limitScope` 等字段。
- 新建 `ZiweiJudgementChain` 与分工裁判器: 宫位、星曜、四化飞星、格局、限运、主题、跨法派、证据分层。
- 从 S/A 级核心法本与系统教材抽取第一批规则节点到 `ziwei_nodes.jsonl` (宫位、星曜、四化、格局、限运)。
- 改造受控 RAG: 规则触发后按 `sourceScope` 检索, 返回 `primaryEvidence` / `secondaryEvidence` / `schoolCommentary` / `caseReference` / `excludedOrUnreadable` 分区。
- 新增 `/api/v1/ziwei/judgement` 输出结构化判盘报告与证据链。
- 改造 `prompts_ziwei.py`: AI 仅根据裁判链与证据链表达, 不得绕过规则直接断盘。
- 改造 `ZiweiTab` 与盘面组件: 展示排盘规则、三方四正高亮、四化飞线、限运引动、裁判意见与分层证据。
- 建立紫微评测回归脚本与错因标签, 接入 contest 紫微通道与 bazi+ziwei 双轨仲裁门禁。

## 影响范围

- 涉及规格: `ziwei-judgement` (新增能力)
- 涉及代码:
  - `code/backend/app/core/ziwei/` (engine, normalize, feixing, interpret, 新建 judgement 子包)
  - `code/backend/app/api/ziwei_router.py`
  - `code/backend/app/core/agent/prompts_ziwei.py`
  - `code/backend/app/benchmark/contest8_eval.py`
  - `code/backend/app/core/fusion/` (bazi+ziwei 仲裁权重)
  - `code/rag/` (build_index, chunker, 紫微检索约束)
  - `code/knowledge/scripts/` (manifest, 规则抽取)
  - `code/knowledge/data/graph/ziwei_nodes.jsonl`
  - `code/frontend/src/` 紫微 Tab 与盘面组件
- 涉及资料:
  - `数据库/11紫微斗数/` (恢复原文 + 分层目录)
  - `report/紫薇斗数最强方案/紫微斗数判盘引擎最强方案.md` (设计依据)
- **不破坏** 现有 `/chart`, `/interpret`, `/chat/init`, `/rag/search` 对外契约; 判盘链以新增接口或可选字段扩展。

## 当前基线 (2026-06-15)

| 维度 | 状态 |
|------|------|
| 排盘 | 公历/农历、真太阳时、闰月/早晚子时、南派/北派/王亭之/壬干四化表, 三合/飞星显示 |
| 飞星 | `compute_flying_mutagens` 可算宫干 outbound/inbound, 未接入裁判链 |
| 解读 | RAG + AI 摘要, 无宫位/四化/限运裁判 |
| 知识库 | 分类清单已完成, manifest 未生成, 工作区原文大部分缺失, 索引仍用旧扁平路径 |
| 规则图谱 | `ziwei_nodes.jsonl` 26 节点 (12 宫 + 14 主星), 不可裁判 |
| 大赛紫微 | `predict_one_ziwei_only` 存在, val 37.5% |
| RAG 索引 | `kb_11_ziwei`, 25 files, 4910 chunks, 12 个 doc 读取失败 |

## 分阶段目标

| 阶段 | 目标 | 门禁 | 状态 |
|------|------|------|------|
| P0 数据与 RAG | 恢复原文 + decrypt + manifest + doc 转换 + 重建索引 + chunk 分层 | 索引失败数归零, spot-check S 级优先 | 待开始 |
| P1 排盘与结构化 | rulesMeta 可审查 + chart enrich (三方四正/空宫借星/庙旺) | normalize 单元测试通过 | 待开始 |
| P2 规则与裁判核心 | 宫位/星曜/四化/格局 judge + 仲裁器 + judgement API | smoke_judgement_ziwei_local 通过 | 待开始 |
| P3 限运与证据 | LimitJudge + 受控 RAG 分区 + prompts 约束 | tieredEvidence 五分区非空 smoke | 待开始 |
| P4 前端报告 | 判盘工作台 UI (飞线/限运/裁判/证据) | 前端可展示主裁/派别/案例三层证据 | 待开始 |
| P5 评测闭环 | contest 紫微回归 + 错因标签 + bazi+ziwei 门禁 | ziwei-only smoke 可跑通且 pred 非空 | 待开始 |
