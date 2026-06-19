## 背景

六爻模块已有确定性装卦 (`LiuyaoEngine`) 和基础用神服务 (`YongShenService`), 但断卦结论仍由 AI 在阅读 RAG 摘录后直接生成。`数据库/02六爻卜筮` 含 S 级四本主裁经典 (增删卜易、卜筮正宗、黄金策、卜筮全书), A 级九本辅助, B 级三本现代讲义; 若不区分证据权限, 曲炜讲义或卦例断语容易压过核心古籍。

八字侧已通过 `BaziJudgementChain` + `arbitrator.py` + `evidence.py` 验证「规则先于检索, 主裁先于辅助」架构。六爻应复用该模式, 但裁判链必须围绕纳甲装卦、占事分类、用神、月建日辰旺衰、原忌仇神、飞伏、动变反吟伏吟、六神与应期建立独立节点, 不能复用八字调候/格局 judge。

## 目标 / 非目标

**目标:**
- 将六爻从「RAG + AI 断卦」升级为 Classic-Grounded Liuyao Reasoning Engine。
- 固化 `数据库/02六爻卜筮` 权威分层与受控 RAG 检索。
- 实现可审查的 `LiuyaoJudgementChain` 与分层证据输出。
- 前端展示判盘报告 (用神链、裁判意见、典籍分区)。
- 建立六爻评测回归与错因标签, 支撑后续迭代。

**非目标:**
- 本变更不修改铜钱/数字/时间起卦的数学规则 (除非门禁证明装卦错误)。
- 不将八字 `BaziJudgementChain` 直接用于六爻卦象 (仅复用架构模式)。
- 不做 LLM 微调或训练。
- 不在本变更内完成全部 64 卦专题规则抽取 (先做 P0-P2 高频节点)。
- 不强制本变更提升大赛全量 200 题准确率 (六爻通道先跑通门禁与子集基线)。

## 技术决策

### 决策 1: 四库分离与 manifest

| 库 | 来源 | 权限 |
|----|------|------|
| 装卦法库 | `LiuyaoEngine` 规则元数据 | 决定卦象结构是否可信 |
| 经典裁判库 | S/A 共 13 文件 (`judge_library`) | 可定理, S 优先于 A |
| 现代补充库 | B 共 3 文件 (`support_library`) | 仅 `explain_only`, 不可推翻 S/A |
| 评测基准库 | Contest 六爻题 | 仅考试, 不进入生产 RAG |

manifest 路径: `code/knowledge/data/sources/liuyao_sources_manifest.json`, 字段对齐八字 `bazi_sources_manifest.json`: `authorityTier`, `libraryRole`, `evidenceRole`, `classic`, `canJudge`, `judgmentPolicy`, `domains`, `topicScope`。

依据: `数据库/02六爻卜筮/_文件分类清单.md` 已有逐文件映射, 本变更将其机器化。

### 决策 1b: 资料解密前置 (decrypt skill)

Windows 环境下公司加密软件可能锁定 `数据库/02六爻卜筮` 文本, 导致 manifest 扫描、RAG `read_document`、规则抽取全部失败。

| 阶段 | 动作 |
|------|------|
| 整理/迁移资料后 | 对目标目录运行 decrypt skill: `file_decrypt.py` |
| `classify_02_sources.py` | 支持 `--decrypt`, 先解密再生成 manifest |
| `build_index.py` 报 empty/error | 先解密, 再单类目重建索引 |
| manifest | 失败文件写 `readStatus=encrypted_or_unreadable`, 不标 `ok` |

脚本路径 (优先全局 skill):

```
C:\Users\liqingfeng\.cursor\skills\decrypt\scripts\file_decrypt.py
```

项目根 `d:\ZY\file_decrypt.py` 可作为等价回退。禁止手写解密逻辑或模拟输出。

### 决策 2: S 级四本分工 (主裁 scope)

| 经典 | evidenceRole | 裁判职责 |
|------|--------------|----------|
| 增删卜易 | core_divination_judge | 用神、旺衰、世应、六冲、应期、实战卦例验证 |
| 卜筮正宗 | core_divination_judge | 纳甲装卦、十八论、飞伏、反吟伏吟、旬空月破 |
| 黄金策 | classic_topic_judge | 分题材占法 (财、官、婚、病、行等) |
| 卜筮全书 | encyclopedic_judge | 综合法度、歌诀互证, 不压过前两本 |

RAG `sourceScope` 按触发的 rule node `classic` 字段白名单检索; 卦例片段 `caseOnly=true` 在 rerank 降权。

### 决策 3: 判盘链顺序

固定链条 (与最强方案一致):

```
chart struct -> topic classify -> yong shen -> wang shuai / sheng ke
-> shi ying / dong bian -> liu shen (aux) -> ying qi -> arbitrate -> evidence -> AI
```

新建包: `code/backend/app/core/liuyao/judgement/`, 结构镜像 `core/judgement/`:

- `chain.py` - `LiuyaoJudgementChain`
- `judges.py` - `TopicJudge`, `YongShenJudge`, `WangShuaiJudge`, `ShengKeJudge`, `ShiYingJudge`, `DongBianJudge`, `YingQiJudge`
- `arbitrator.py` - `LiuyaoArbiter`
- `evidence.py` - 分层证据汇总
- `models.py` - pydantic/dataclass 输出

卦象增强 (在 `engine.py` 或 `chart_enrich.py`):
- 旬空、月破、飞伏、变爻化进化退、回头生克、反吟伏吟标记
- 每爻 `lineStrength`, `kongPoState`, `dongBianTarget`, `riskFlags`

### 决策 4: 用神裁判优先于 AI

`YongShenService` 改造:
1. `TopicJudge` 根据问事归类 (规则节点 + 扩展 `KEYWORD_RULES`)
2. `YongShenJudge` 按卦中六亲分布、伏神、用神不上卦换用神规则定位爻位
3. AI 推断降为 fallback, 输出 `source=ai|rule`, 用户 override 保留审计

第一批规则来源: 《增删卜易》用神章 + 《卜筮正宗》用神分类定例。

### 决策 5: 受控 RAG

扩展 `code/rag` 检索 filters (或 backend rag provider):
- `authorityTier` in (S, A)
- `classic` whitelist per rule node
- `topicScope` match
- `caseOnly` downrank
- B 级 `explain_only` 仅作 `modernSupport`

`LiuyaoInterpretService.build_query` 改为: 裁判链输出 `ragQuery` + `sourceScope`, 不再仅拼卦名+用神关键词。

返回 schema 对齐八字 `tieredEvidence`:
```json
{
  "primaryEvidence": [],
  "secondaryEvidence": [],
  "caseReference": [],
  "modernSupport": [],
  "excludedOrLowTrust": []
}
```

### 决策 6: API 与前端

新增 `POST /api/v1/liuyao/judgement`:
- 输入: `chart`, `yongShen` (可选, 可覆盖), `question`
- 输出: `judgement` (裁判链), `tieredEvidence`, `confidence`, `conflicts`

现有 `POST /interpret` 内部调用 judgement + AI, 向后兼容。

前端新增 `LiuyaoJudgementPanel` (可参考 `BaziJudgementPanel`):
- 顶部: 起卦规则、月建日辰、用神
- 中部: 卦象高亮 (用神/世应/动爻/空破)
- 下部: 裁判分区 + 分层典籍 + AI 报告

### 决策 7: 规则图谱扩充策略

`liuyao_nodes.jsonl` 分批扩充:

| 批次 | 来源 | 节点类型 | 目标数量 |
|------|------|----------|----------|
| B1 | 增删卜易 | yong_shen, wang_shuai, liu_chong, ying_qi | >= 30 |
| B2 | 卜筮正宗 | fei_fu, fan_yin, fu_yin, xun_kong, yue_po | >= 25 |
| B3 | 黄金策 | topic_divination (财/官/婚/病/行) | >= 20 |

节点字段对齐 `node.schema.json`, 增加 `domain=liuyao`, `topic`, `classic`, `conditions`, `confidenceBaseline`.

### 决策 8: 评测与错因

脚本: `code/backend/scripts/run_liuyao_regression_gate.py`
- 调用 `predict_one_liuyao_only` 或新 judgement-aware predictor
- 输出 `errorLabels`: `wrong_topic_class`, `wrong_yong_shen`, `ignore_yue_jian`, `ignore_kong_po`, `wrong_dong_bian`, `case_overfit`, `modern_notes_override` 等
- 评测库与 `kb_02_liuyao` 生产检索隔离 (大赛题不得入索引)

门禁: P4 完成时, liuyao-only smoke (>= 5 题) 产生非空 `liuyaoPred` 且 judgement API smoke 通过。

## 风险与权衡

- **规则抽取工作量**: 古文节点需人工校对; 先做高频用神/空破/六冲, 专题占法后补。
- **与 AI fallback 并存**: 规则未覆盖时降级 AI + 低置信度, 避免假确定性。
- **索引路径变更**: 重建 `kb_02_liuyao` 需重跑 `build_index.py`, 部署时同步 RAG 服务。
- **大赛六爻题量少**: 先建门禁机制, 不追求一次大幅提升全量准确率。
- **B 级 doc 文件**: 2 个 `.doc` 已在索引 ok; manifest 标记 `explain_only` 即可。

## 迁移计划

1. **P0**: manifest + 重建索引 + spot-check (无用户可见行为变化)
2. **P1**: 用神/占事规则 + 单元测试 (YongShenEditor 显示 rule source)
3. **P2**: judgement chain + API + prompts 约束 (interpret 质量提升)
4. **P3**: 前端判盘报告 + tiered evidence 展示
5. **P4**: regression gate + contest liuyao 子集基线记录

每阶段合并前:
- `pytest` 新增 liuyao judgement 测试通过
- RAG health 200
- 对应 smoke JSON 写入 `report/六爻卜筮最强方案/` 或 `code/backend/data/reports/`

## 待决问题

- judgement 是独立端点还是仅扩展 interpret payload? **默认: 新增 `/judgement`, interpret 内部复用**。
- 伏神/卦身是否纳入 P2? **P2 做旬空月破+动变; 伏神放 P2 末或 P3 初**。
- contest 六爻题如何识别? **沿用 `paipan_to_liuyao_input` + 现有 liuyao MCQ parts, 后续加 `theme=liuyao_suitable` 标注**。
