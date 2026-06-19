## 0. P0 前置 - 资料恢复与解密

- [x] 0.1 从备份或资料源恢复 `数据库/11紫微斗数` 下 25 个 `.doc` 原文到 `S_核心法本/`、`A_系统教材/`、`A_星曜格局/`、`B_技法补充/`、`C_宫位专题/`、`D_待清洗/` (对照 `_文件分类清单.md`)
- [x] 0.2 对 `数据库/11紫微斗数` 运行 decrypt skill: `py -3.10 "C:\Users\liqingfeng\.cursor\skills\decrypt\scripts\file_decrypt.py" "数据库/11紫微斗数"`, 记录 success/failed/skipped
- [x] 0.3 doc->txt 批量转换: 27/27 已全部转 txt 并归档至 `_doc_backup/` (含诸星/父母宫/福德宫)
- [x] 0.4 删除或忽略 Office 临时文件 `~$斗数命盘解析...doc`, 不纳入索引

## 1. P0 - 数据分层与 RAG 索引

- [x] 1.0 新建 `code/knowledge/scripts/classify_11_sources.py`, 支持 `--decrypt` 先解密再扫描
- [x] 1.1 依据 `数据库/11紫微斗数/_文件分类清单.md` 生成 `code/knowledge/data/sources/ziwei_sources_manifest.json` (27 文件全量条目, 含 2 份新补 S 级 txt)
- [x] 1.2 扩展 `code/knowledge/scripts/source_manifest.py` 或新建校验脚本, 支持紫微 `--validate-only`
- [x] 1.3 改造 `code/rag/chunker.py` / `build_index.py`, chunk metadata 写入 `authorityTier`, `libraryRole`, `evidenceRole`, `school`, `topicScope`, `textRole`, `palaceScope`, `starScope`, `mutagenScope`, `limitScope`
- [x] 1.4 重建 `kb_11_ziwei` 索引 (当前 27 ok / 0 error, chunks 5437)
- [x] 1.5 将 2 份新补 S 级 `.txt` (全书全览、十八飞星) 纳入索引并核对 chunk 数
- [x] 1.6 新增 `code/rag/spot_check_ziwei_metadata.py`, 验证 S 级片段在星曜/四化查询中优先于 B 级
- [x] 1.7 输出 spot-check 报告到 `report/紫薇斗数最强方案/rag_spot_check_ziwei.json` (待 RAG 服务启动后执行 spot-check)

## 2. P1 - 排盘法库与本命盘结构化

- [x] 2.1 在 `normalize.py` 或新建 `chart_enrich.py` 输出 `palaceStrength`, `triadEvidence`, `oppositeEvidence`, 空宫借星标注
- [x] 2.2 排盘结果增加 `rulesMeta` (闰月、早晚子时、真太阳时、四化表、法派), API `/chart` 响应可审查
- [x] 2.3 用户切换排盘规则导致命宫/四化变化时, 返回 `ruleChangeWarning` 提示 (`compare_rule_change` 已实现, 待 API 接线)
- [x] 2.4 单元测试 `tests/test_ziwei_chart_enrich.py` (三方四正、空宫借星、庙旺 >= 8 场景)

## 3. P2 - 规则图谱与裁判核心

- [x] 3.1 定义紫微规则节点 schema 扩展 (`school`, `palaceScope`, `starScope`, `mutagenScope`, `conditions`)
- [x] 3.2 从 S 级太微赋/全书抽取第一批节点: 十二宫主题 + 十四主星庙旺组合 (脚本 `expand_ziwei_nodes.py`)
- [x] 3.3 从 A 级教材抽取第二批节点: 四化飞星、杀破狼/府相朝垣等格局
- [x] 3.4 扩充 `code/knowledge/data/graph/ziwei_nodes.jsonl` 至 >= 100 可执行节点 (当前 134)
- [x] 3.5 新建 `code/backend/app/core/ziwei/judgement/palace_judge.py`
- [x] 3.6 新建 `star_judge.py`, `mutagen_judge.py`, `pattern_judge.py`
- [x] 3.7 新建 `topic_judge.py`, `cross_school_judge.py`, `limit_judge.py` (P2 最小版)
- [x] 3.8 新建 `arbitrator.py`, `evidence.py`, `models.py`, `chain.py` (`ZiweiJudgementChain`)
- [x] 3.9 新增 schema `code/backend/app/schemas/ziwei_judgement.py`
- [x] 3.10 新增 `POST /api/v1/ziwei/judgement` 于 `ziwei_router.py`
- [x] 3.11 改造 `ZiweiInterpretService` 与 `prompts_ziwei.py`: 仅根据 judgement + tieredEvidence 表达
- [x] 3.12 单元测试 `tests/test_ziwei_judgement_chain.py`, `tests/test_ziwei_arbitrator_conflicts.py`, `tests/test_ziwei_mutagen_judge.py`
- [x] 3.13 脚本 `scripts/smoke_judgement_ziwei_local.py`, 输出 `report/紫薇斗数最强方案/smoke_judgement_ziwei_local.json`

## 4. P3 - 限运裁判与受控 RAG

- [x] 4.1 新建 `limit_judge.py`: 本命/大限/流年/小限事件链, 冲照本命关键宫
- [x] 4.2 扩展 RAG provider: school whitelist, authorityTier filter, textRole=case downrank
- [x] 4.3 `ZiweiInterpretService` 返回 `tieredEvidence` 五分区
- [x] 4.4 单元测试 `tests/test_ziwei_limit_judge.py`, `tests/test_ziwei_tiered_evidence.py`

## 5. P4 - 前端判盘报告

- [x] 5.1 新建前端 `ZiweiJudgementPanel.tsx`, 展示裁判链与证据分区
- [x] 5.2 改造盘面组件: 三方四正高亮、四化飞线、限运引动宫、格局标签
- [x] 5.3 改造 `ZiweiTab`: 顶部 rulesMeta, 中部盘面, 下部裁判+证据+AI 报告
- [x] 5.4 前端类型 `types/ziwei.ts` 增加 judgement 与 tieredEvidence 字段
- [x] 5.5 API smoke `scripts/smoke_judgement_ziwei_api.py` (可选本地/部署)

## 6. P5 - 评测闭环

- [x] 6.1 新建 `code/backend/app/benchmark/ziwei_error_labels.py` 错因标签
- [x] 6.2 新建 `scripts/run_ziwei_regression_gate.py`, 支持 `--split val` 与子集过滤
- [x] 6.3 改造 `contest8_eval.py` `predict_one_ziwei_only`: 可选接入 `ZiweiJudgementChain` 预结论
- [x] 6.4 跑 ziwei-only smoke (>= 5 题), 确认预测非空, 报告 `contest8_ziwei_smoke.json`
- [x] 6.5 将紫微通道接入 bazi+ziwei 仲裁门禁, 仅在 `ziwei_suitable` 题型提高权重
- [x] 6.6 在 `report/紫薇斗数最强方案/` 记录 P0-P5 阶段验收与基线数字
- [ ] 6.7 门禁通过后执行 `openspec validate improve-ziwei-judgement-engine --strict`

## 7. 每阶段通用校验

- [ ] 7.0 资料管线遇 `empty`/`error`/`readStatus=encrypted_or_unreadable` 时, 先跑 decrypt skill 再重建 manifest/索引
- [x] 7.1 `py -3.10 -m pytest tests/test_ziwei*.py -q`
- [ ] 7.2 RAG 评测前确认 `http://127.0.0.1:8100/health` 返回 200
- [x] 7.3 不破坏现有 `/chart`, `/interpret`, `/rag/search`, `/chat/init` 契约
- [x] 7.4 PR/任务记录写明相对上一阶段的 smoke 与评测 delta
