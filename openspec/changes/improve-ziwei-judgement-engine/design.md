## 背景

紫微模块已有确定性排盘 (`ZiweiEngine` + `iztro-py`) 和基础飞星计算 (`compute_flying_mutagens`), 但断盘结论仍由 AI 在阅读 RAG 摘录后直接生成。`数据库/11紫微斗数` 规划含 S 级核心法本 3、A 级系统教材/星曜格局 7、B 级技法 4、C 级宫位专题 11、D 级待清洗 2; 若不区分证据权限与法派边界, 现代讲义或单宫口诀容易压过《太微赋》《紫微斗数全书》等主裁经典。

八字侧已通过 `BaziJudgementChain` + `arbitrator.py` + `evidence.py` 验证「规则先于检索, 主裁先于辅助」架构。六爻侧 `LiuyaoJudgementChain` 已落地 P0-P3。紫微应复用该模式, 但裁判链必须围绕十二宫主题、十四主星组合、四化飞星方向、格局成立/破格、大限流年事件链、三合/飞星法派差异建立独立节点, **不能** 复用八字调候/格局 judge。

## 目标 / 非目标

**目标:**
- 将紫微从「RAG + AI 断盘」升级为 Classic-Grounded Ziwei Reasoning Engine。
- 恢复 `数据库/11紫微斗数` 原文, 固化权威分层与受控 RAG 检索。
- 实现可审查的 `ZiweiJudgementChain` 与分层证据输出。
- 前端展示判盘报告 (排盘规则、三方四正、四化飞线、限运引动、裁判意见、典籍分区)。
- 建立紫微评测回归与错因标签, 支撑后续迭代与 bazi+ziwei 双轨优化。

**非目标:**
- 本变更不修改 `iztro-py` 安星数学 (除非门禁证明排盘规则错误)。
- 不将 `BaziJudgementChain` 直接用于紫微宫星 (仅复用架构模式与 fusion 仲裁接口)。
- 不做 LLM 微调或训练。
- 不在本变更内完成全部格局与限运规则抽取 (先做 P0-P2 高频节点)。
- 不强制本变更提升大赛全量 200 题准确率 (紫微通道先跑通门禁与子集基线)。
- 不自动抓取未授权现代书籍全文 (仅记录 `_现代资料补充清单.md` 待用户合法提供)。

## 技术决策

### 决策 1: 四库分离与 manifest

| 库 | 来源 | 权限 |
|----|------|------|
| 排盘法库 | `ZiweiEngine` + `rules.py` 规则元数据 | 决定盘结构是否可信 |
| 经典裁判库 | S/A 共 10 文件 (`judge_library`) | 可定理, S 优先于 A |
| 技法辅助库 | B 共 4 文件 (`support_library`) | 仅 `explain_only`, 不可推翻 S/A |
| 宫位专题库 | C 共 11 文件 (`topic_library`) | 仅对应宫位主题辅助 |
| 评测基准库 | Contest 紫微题 + 人工命例 | 仅考试, 不进入生产 RAG |

manifest 路径: `code/knowledge/data/sources/ziwei_sources_manifest.json`, 字段对齐八字 `bazi_sources_manifest.json`, 并增加紫微特有字段: `school` (sanhe/feixing/hezhong/general), `topicScope`, `palaceScope`, `starScope`, `mutagenScope`, `limitScope`, `readStatus`。

依据: `数据库/11紫微斗数/_文件分类清单.md` 已有逐文件映射, 本变更将其机器化。

### 决策 1b: 资料解密前置 (decrypt skill)

Windows 环境下公司加密软件可能锁定 `数据库/11紫微斗数` 下 `.doc`/`.txt`, 导致 manifest 扫描、RAG `read_document`、规则抽取全部失败。整理记录显示曾成功解密 26 个文件, 但后续恢复原文时仍可能再次遇锁。

| 阶段 | 动作 |
|------|------|
| 恢复/整理资料后 | 对目标目录运行 decrypt skill: `file_decrypt.py` |
| `classify_11_sources.py` (新建) | 支持 `--decrypt`, 先解密再生成 manifest |
| `build_index.py` 报 empty/error | 先解密, 再单类目重建索引 |
| manifest | 失败文件写 `readStatus=encrypted_or_unreadable`, 不标 `ok` |

脚本路径 (优先全局 skill):

```
C:\Users\liqingfeng\.cursor\skills\decrypt\scripts\file_decrypt.py
```

项目根 `d:\ZY\file_decrypt.py` 可作为等价回退。禁止手写解密逻辑或模拟输出。

decrypt skill 工作流:
1. 确认目标路径存在 (文件或目录)
2. 运行 `file_decrypt.py` 递归解密
3. 读取 `[OK]`/`[FAIL]`/`[SKIP]` 输出
4. 报告 success/failed/skipped 统计
5. `[FAIL]` 文件保持原状, 不进入主裁检索

### 决策 2: S/A 级分工 (主裁 scope)

| 层级 | 代表资料 | evidenceRole | 裁判职责 |
|------|----------|--------------|----------|
| S | 太微赋精解, 全书维基全览, 十八飞星照胆经 | primary_classic | 宫义、星曜骨架、格局与重要断法 |
| A | 大德山人精成, 令东来体系, 星情细论, 格局研究 | systematic_support / star_judge / pattern_judge | 系统教材与派别方法, 辅助主裁 |
| B | 庖丁解牛, 论命不求人等 | modern_explanation | 仅白话与技法补充 |
| C | 十二宫论命要诀 | palace_topic_support | 仅对应宫位主题 |
| D | 阳宅风水, 过短婚恋专题 | cross_topic / low_signal | 默认排除 |

RAG `sourceScope` 按触发的 rule node `school`, `topic`, `palaceScope` 白名单检索; 命例片段 `textRole=case` 在 rerank 降权。

### 决策 3: 判盘链顺序

固定链条 (与最强方案一致):

```
input validate -> chart rules meta -> natal struct enrich
-> palace judge -> star judge -> mutagen judge -> pattern judge
-> limit judge -> topic judge -> cross-school judge -> arbitrate -> evidence -> AI
```

新建包: `code/backend/app/core/ziwei/judgement/`, 结构镜像 `core/judgement/` 与 `core/liuyao/judgement/`:

- `chain.py` - `ZiweiJudgementChain`
- `judges.py` - `PalaceJudge`, `StarJudge`, `MutagenJudge`, `PatternJudge`, `LimitJudge`, `TopicJudge`, `CrossSchoolJudge`
- `arbitrator.py` - `ZiweiArbiter`
- `evidence.py` - 分层证据汇总
- `models.py` - pydantic/dataclass 输出

本命盘增强 (在 `normalize.py` 或 `chart_enrich.py`):
- 十二宫 `palaceStrength`, `majorPattern`, `mutagenState`
- 三方四正 `triadEvidence`, 对宫 `oppositeEvidence`, 夹宫标记
- 空宫借对宫主星规则显式标注
- 庙旺陷、辅煞平衡 `supportMaleficBalance`, `riskFlags`

### 决策 4: 四化飞星裁判

`feixing.compute_flying_mutagens` 已产出 outbound/inbound, 本变更将其转为有向规则节点:
- `夫妻宫化忌入命宫`
- `财帛宫化禄入官禄`
- `大限命宫飞忌冲本命夫妻`

`MutagenJudge` 必须输出方向性 (从何宫来、落何宫、冲何宫、本命/大限/流年 scope), 不能只说「有化忌」。

用户选择法派 (`sanhe` / `feixing`) 决定主裁权重; 另一派作 `schoolCommentary` 辅助视角。

### 决策 5: 受控 RAG

扩展 `code/rag` 检索 filters:
- `authorityTier` in (S, A) 用于主裁
- `school` match per rule node
- `topicScope`, `palaceScope`, `starScope` match
- `textRole=case` downrank
- B/C 级按 `judgmentPolicy` 限制分区

`ZiweiInterpretService` 改为: 裁判链输出 `ragQuery` + `sourceScope`, 不再仅拼星名+宫位关键词。

返回 schema:
```json
{
  "primaryEvidence": [],
  "secondaryEvidence": [],
  "schoolCommentary": [],
  "caseReference": [],
  "excludedOrUnreadable": []
}
```

### 决策 6: API 与前端

新增 `POST /api/v1/ziwei/judgement`:
- 输入: `chart` (或 birthData + rules), 可选 `question`, `targetYear`, `school`
- 输出: `judgement` (裁判链), `tieredEvidence`, `rulesMeta`, `confidence`, `conflicts`

现有 `POST /interpret` 内部调用 judgement + AI, 向后兼容。

前端新增 `ZiweiJudgementPanel` (可参考 `BaziJudgementPanel`):
- 顶部: 排盘规则、真太阳时、命宫身宫、当前大限流年、法派
- 中部: 十二宫盘面、三方四正高亮、四化飞线、限运引动宫
- 下部: 裁判分区 + 分层典籍 + AI 报告

### 决策 7: 规则图谱扩充策略

`ziwei_nodes.jsonl` 分批扩充:

| 批次 | 来源 | 节点类型 | 目标数量 |
|------|------|----------|----------|
| B1 | 太微赋 + 全书 | palace, star (庙旺组合) | >= 40 |
| B2 | 大德山人/令东来 | mutagen, pattern | >= 35 |
| B3 | 星情细论/格局研究 | pattern, malefic_combo | >= 25 |
| B4 | 宫位要诀 (转换后) | palace_topic | >= 12 |

节点字段对齐 `node.schema.json`, 增加 `domain=ziwei`, `school`, `palaceScope`, `starScope`, `mutagenScope`, `conditions`, `confidenceBaseline`.

### 决策 8: 评测与错因

脚本: `code/backend/scripts/run_ziwei_regression_gate.py`
- 调用 `predict_one_ziwei_only` 或新 judgement-aware predictor
- 输出 `errorLabels`: `wrong_chart_rule`, `ignore_body_palace`, `single_star_overfit`, `ignore_triad`, `ignore_opposite`, `wrong_mutagen_direction`, `wrong_limit_scope`, `school_mixing`, `case_overfit`, `overconfident_claim` 等
- 评测库与 `kb_11_ziwei` 生产检索隔离

门禁: P5 完成时, ziwei-only smoke (>= 5 题) 产生非空预测且 judgement API smoke 通过。

## 风险与权衡

- **原文缺失**: 工作区仅 2 份 S 级 txt, 25 个 doc 需从备份恢复; P0 阻塞后续所有阶段。
- **doc 读取失败**: 12 个宫位/星情 doc 需转换格式, 否则 C 级专题库无法入库。
- **法派冲突**: 三合/飞星结论可能相反; 必须用户显式选法派 + 仲裁器标注差异。
- **规则抽取工作量**: 古文节点需人工校对; 先做命宫/夫妻/官禄 + 四化飞忌 + 杀破狼等高频格局。
- **与 AI fallback 并存**: 规则未覆盖时降级 AI + 低置信度, 避免假确定性。
- **大赛紫微题量少**: 先建门禁机制, 不追求一次大幅提升全量准确率。

## 迁移计划

1. **P0**: 恢复原文 + decrypt + manifest + doc 转换 + 重建索引 + spot-check
2. **P1**: chart enrich + rulesMeta 报告展示 (无裁判行为变化)
3. **P2**: 宫位/星曜/四化/格局 judge + 仲裁器 + judgement API + prompts 约束
4. **P3**: LimitJudge + 受控 RAG 分区
5. **P4**: 前端判盘工作台 + tiered evidence 展示
6. **P5**: regression gate + contest ziwei 子集基线 + bazi+ziwei 权重调优

每阶段合并前:
- `pytest` 新增 ziwei judgement 测试通过
- RAG health 200
- 对应 smoke JSON 写入 `report/紫薇斗数最强方案/` 或 `code/backend/data/reports/`

## 待决问题

- judgement 是独立端点还是仅扩展 interpret payload? **默认: 新增 `/judgement`, interpret 内部复用**。
- 身宫裁判是否独立于命宫? **P2 做身宫主题为后天着力点, 与命宫格局分开仲裁**。
- contest 紫微题如何识别? **沿用 `predict_one_ziwei_only` + 后续加 `theme=ziwei_suitable` 与 `mustCheckPalaces/Stars` 标注**。
- 工作区 doc 原文从哪恢复? **优先 `backups/knowledge-base_*` 或用户提供的资料源, P0 任务 0.1 明确**。
