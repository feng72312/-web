## 1. P0 - 数据分层与 RAG 索引 (基础)

- [x] 1.0 `classify_02_sources.py --decrypt` 接入 decrypt skill (`file_decrypt.py`), 整理前可批量解密
- [x] 1.1 依据 `数据库/02六爻卜筮/_文件分类清单.md` 生成 `code/knowledge/data/sources/liuyao_sources_manifest.json` (16 文件全量条目)
- [x] 1.2 新增 `code/knowledge/scripts/source_manifest_liuyao.py` 或扩展现有 `source_manifest.py` 支持六爻校验
- [x] 1.3 改造 `code/rag/chunker.py` / `build_index.py`, chunk metadata 写入 `authorityTier`, `libraryRole`, `evidenceRole`, `classic`, `topicScope`, `textRole`, `caseOnly`
- [x] 1.4 重建 `kb_02_liuyao` 索引, 使用 `S_主裁经典/`、`A_辅助经典/`、`B_现代技法/` 新路径, 核对 16 files / chunks 数
- [x] 1.5 新增 `code/rag/spot_check_liuyao_metadata.py`, 验证 S 级片段在用神/旺衰查询中优先于 B 级
- [x] 1.6 输出 spot-check 报告到 `report/六爻卜筮最强方案/rag_spot_check_liuyao.json`

## 2. P1 - 规则图谱与用神裁判

- [x] 2.1 定义六爻规则节点 schema 扩展 (在 `node.schema.json` 或 liuyao 专用注释中明确 `domain`, `topic`, `classic`, `conditions`)
- [x] 2.2 从《增删卜易》抽取第一批节点: 用神章、旺衰、六冲 (脚本 `extract_liuyao_zengshan.py` 或手工 JSONL)
- [x] 2.3 从《卜筮正宗》抽取第二批节点: 旬空、月破、飞伏、反吟伏吟
- [x] 2.4 扩充 `code/knowledge/data/graph/liuyao_nodes.jsonl` 至 >= 55 可执行节点 (含原 64 卦名保留)
- [x] 2.5 新建 `code/backend/app/core/liuyao/judgement/topic_judge.py` (占事分类)
- [x] 2.6 新建 `code/backend/app/core/liuyao/judgement/yong_shen_judge.py` (规则用神定位)
- [x] 2.7 改造 `YongShenService`: 规则优先, AI fallback, 输出 `source` 与 `confidence`
- [x] 2.8 单元测试 `tests/test_liuyao_topic_judge.py`, `tests/test_liuyao_yong_shen_judge.py` (>= 10 场景)

## 3. P2 - 判盘链核心与 API

- [x] 3.1 新建 `chart_enrich.py`: 旬空、月破、动变化进化退、回头生克、六冲标记
- [x] 3.2 新建 `judgement/wang_shuai_judge.py`, `sheng_ke_judge.py`, `dong_bian_judge.py`, `shi_ying_judge.py`
- [x] 3.3 新建 `judgement/ying_qi_judge.py`, `liu_shen_judge.py` (六神仅辅助)
- [x] 3.4 新建 `judgement/arbitrator.py`, `evidence.py`, `models.py`, `chain.py` (`LiuyaoJudgementChain`)
- [x] 3.5 新增 schema `code/backend/app/schemas/liuyao_judgement.py`
- [x] 3.6 新增 `POST /api/v1/liuyao/judgement` 于 `liuyao_router.py`
- [x] 3.7 改造 `LiuyaoInterpretService` 与 `prompts_liuyao.py`: 仅根据 judgement + tieredEvidence 表达
- [x] 3.8 单元测试 `tests/test_liuyao_judgement_chain.py`, `tests/test_liuyao_arbitrator_conflicts.py`
- [x] 3.9 脚本 `scripts/smoke_judgement_liuyao_local.py`, 输出 `report/六爻卜筮最强方案/smoke_judgement_liuyao_local.json`

## 4. P3 - 受控 RAG 与前端报告

- [x] 4.1 扩展 RAG provider: classic whitelist, authorityTier filter, caseOnly downrank
- [x] 4.2 `LiuyaoInterpretService` 返回 `tieredEvidence` 五分区
- [x] 4.3 新建前端 `LiuyaoJudgementPanel.tsx`, 展示裁判链与证据分区
- [x] 4.4 改造 `HexagramBoard` / `LiuyaoTab`: 高亮用神、世应、动爻、旬空月破
- [x] 4.5 前端类型 `types/liuyao.ts` 增加 judgement 与 tieredEvidence 字段
- [x] 4.6 API smoke `scripts/smoke_judgement_liuyao_api.py` (可选本地/部署)

## 5. P4 - 评测闭环

- [x] 5.1 新建 `code/backend/app/benchmark/liuyao_error_labels.py` 错因标签
- [x] 5.2 新建 `scripts/run_liuyao_regression_gate.py`, 支持 `--split val` 与子集过滤
- [x] 5.3 改造 `contest8_eval.py` `predict_one_liuyao_only`: 可选接入 `LiuyaoJudgementChain` 预结论
- [x] 5.4 跑 liuyao-only smoke (>= 5 题), 确认 `liuyaoPred` 非空, 报告 `contest8_liuyao_smoke.json`
- [x] 5.5 在 `report/六爻卜筮最强方案/` 记录 P0-P4 阶段验收与基线数字
- [x] 5.6 门禁通过后执行 `openspec validate improve-liuyao-judgement-engine --strict`

## 6. 每阶段通用校验

- [x] 6.0 资料管线遇 `empty`/`error`/`readStatus=encrypted_or_unreadable` 时, 先跑 decrypt skill 再重建 manifest/索引
- [x] 6.1 `py -3.10 -m pytest tests/test_liuyao*.py -q` (30 项通过)
- [x] 6.2 RAG 评测前确认 `http://127.0.0.1:8100/health` 返回 200 (smoke 实测通过)
- [ ] 6.3 不破坏现有 `/divine`, `/infer-yong-shen`, `/interpret`, `/chat/init` 契约 (回归 `smoke_test_apis` 或等价 smoke)
- [x] 6.4 PR/任务记录写明相对上一阶段的 smoke 与评测 delta (`P0-P4_阶段验收.md`)
