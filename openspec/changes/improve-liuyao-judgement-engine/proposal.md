# 变更: 六爻 Classic-Grounded 判盘引擎升级

## 背景与动机

六爻模块当前已具备 `LiuyaoEngine` 纳甲装卦、`YongShenService` 用神推断、`LiuyaoInterpretService` RAG 检索与 AI 解读, 但断卦仍停留在「起卦 + 向量检索 + AI 自由发挥」阶段。`数据库/02六爻卜筮` 已完成首轮整理 (S 4 / A 9 / B 3, 共 16 文件), 历史 RAG 索引 `kb_02_liuyao` 为 5306 chunk, 却尚未建立 source manifest、片段级权威分层与可执行裁判链。

与八字 `BaziJudgementChain` 和紫微最强方案相比, 六爻缺少: 占事分类裁判、用神规则裁判、旺衰生克裁判、世应动变裁判、应期裁判、仲裁器、分层证据链输出与闭卷评测门禁。现有 `liuyao_nodes.jsonl` 仅有 1 个用神泛节点 + 64 卦名节点, `safeAutoAnswer=false`, 不能真正裁判。大赛评测 `predict_one_liuyao_only` 已存在, 但报告里 `liuyaoPred` 多为空, 无法支撑持续优化。

依据 `report/六爻卜筮最强方案/六爻判盘引擎最强方案.md`, 需要将六爻升级为「经典规则裁判、证据链可追溯、AI 只负责表达」的专业断卦系统, 并与八字/紫微形成可互证的多术架构。

## 变更内容

- 建立六爻 **四库分离**: 装卦法库、经典裁判库 (`judge_library` 13)、现代补充库 (`support_library` 3)、评测基准库 (与生产 RAG 隔离)。
- 生成 `liuyao_sources_manifest.json`, 固化 `数据库/02六爻卜筮` S/A/B 分层与 `canJudge` / `judgmentPolicy` 策略。
- 重建 `kb_02_liuyao` 索引, 同步 `S_主裁经典/`、`A_辅助经典/`、`B_现代技法/` 新路径, chunk metadata 写入 `authorityTier`, `textRole`, `topicScope`, `caseOnly` 等字段。
- 接入 **decrypt skill** 前置流程: `classify_02_sources.py --decrypt` 在 manifest/索引前批量解密, 防止公司加密导致资料不可用。
- 新建 `LiuyaoJudgementChain` 与分工裁判器: 占事分类、用神、旺衰生克、世应动变、六神辅助、应期、专题占法。
- 从 S 级四本核心书抽取第一批规则节点到 `liuyao_nodes.jsonl` (用神、旬空月破、飞伏、六冲、专题占法)。
- 改造受控 RAG: 规则触发后按 `sourceScope` 检索, 返回 `primaryEvidence` / `secondaryEvidence` / `caseReference` / `modernSupport` 分区。
- 新增 `/api/v1/liuyao/judgement` (或扩展现有 interpret) 输出结构化判盘报告与证据链。
- 改造 `prompts_liuyao.py`: AI 仅根据裁判链与证据链表达, 不得绕过规则直接断吉凶。
- 改造前端 `LiuyaoTab`: 展示用神链、裁判意见、分层证据与装卦规则。
- 建立六爻评测回归脚本与错因标签, 接入 contest 六爻通道门禁。

## 影响范围

- 涉及规格: `liuyao-judgement` (新增能力)
- 涉及代码:
  - `code/backend/app/core/liuyao/` (engine, yong_shen, interpret, 新建 judgement 子包)
  - `code/backend/app/api/liuyao_router.py`
  - `code/backend/app/core/agent/prompts_liuyao.py`
  - `code/backend/app/benchmark/contest8_eval.py`
  - `code/rag/` (build_index, chunker, bazi_rag_engine 或六爻专用检索约束)
  - `code/knowledge/scripts/` (manifest, 规则抽取)
  - `code/knowledge/data/graph/liuyao_nodes.jsonl`
  - `code/frontend/src/tabs/LiuyaoTab.tsx` 及六爻组件
- 涉及资料:
  - `数据库/02六爻卜筮/` (已整理, 不移动文件)
  - `report/六爻卜筮最强方案/六爻判盘引擎最强方案.md` (设计依据)
- **不破坏** 现有 `/divine`、`/infer-yong-shen`、`/chat/init` 对外契约; 判盘链以新增接口或可选字段扩展。

## 当前基线 (2026-06-15 变更前)

| 维度 | 状态 |
|------|------|
| 装卦 | 铜钱/数字/时间起卦 + 正宗纳甲, `meta.rules=卜筮正宗纳甲` |
| 用神 | 关键词规则 + AI 推断, 无规则裁判 |
| 解读 | RAG + AI 摘要, 无旺衰/动变/应期裁判 |
| 知识库 | 16 文件已分层目录, manifest 未生成, 索引仍用旧扁平路径 |
| 规则图谱 | `liuyao_nodes.jsonl` 65 节点 (1 用神 + 64 卦名), 不可裁判 |
| 大赛六爻 | `predict_one_liuyao_only` 存在, `liuyaoPred` 报告多为空 |
| RAG 索引 | `kb_02_liuyao`, 16 files, 5306 chunks, 全部 ok |

## 验收基线 (2026-06-18 变更后)

| 维度 | 状态 |
|------|------|
| manifest | `liuyao_sources_manifest.json`, 16 文件, `readStatus` 齐全 |
| RAG | `kb_02_liuyao` 5306 chunks, S/A/B 路径, spot-check 通过 |
| 规则图谱 | `liuyao_nodes.jsonl` >= 55 规则节点 + 64 卦名 |
| 判盘链 | `LiuyaoJudgementChain` 8 judges, `/api/v1/liuyao/judgement` |
| 前端 | `LiuyaoJudgementPanel` + `HexagramBoard` 空破高亮 |
| 单测 | `pytest` 六爻相关 30 项通过 |
| 离线门禁 | `coverageRate=1.0` (val 10 题) |
| contest smoke | val 5 题 `liuyaoPred` 5/5 非空, 准确率 60% (3/5) |
| 错因 Top | `wrong_topic_class=2`, `wrong_yong_shen=2` |

## 分阶段目标

| 阶段 | 目标 | 门禁 | 状态 |
|------|------|------|------|
| P0 数据与 RAG | manifest + 重建索引 + chunk 分层 | spot-check 主裁片段优先于 B 级 | **已完成** |
| P1 规则与用神 | 占事分类 + 用神裁判 + 第一批规则节点 | 用神单元测试 >= 10 条通过 | **已完成** |
| P2 判盘链核心 | 旺衰/生克/动变裁判 + 仲裁器 + judgement API | smoke_judgement_local 通过 | **已完成** |
| P3 证据与前端 | 受控 RAG 分区 + 判盘报告 UI | 前端可展示主裁/案例/现代三层证据 | **已完成** |
| P4 评测闭环 | contest 六爻回归 + 错因标签 | liuyao-only 子集可跑通且非空 pred | **已完成** |
