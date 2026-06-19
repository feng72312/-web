# 阶段01-三库分离与RAG索引记录

## 阶段目标

将 manifest 三库分层真正落到 RAG 索引, 完成磁盘/manifest/index_report 三方对账, 验证 chunk metadata 含 authorityTier/evidenceRole/libraryRole/canJudge, 抽测主裁优先与命例不越权喵

## 输入资料

- `code/knowledge/scripts/classify_01_sources.py`
- `code/knowledge/scripts/source_manifest.py`
- `code/knowledge/data/sources/bazi_sources_manifest.json`
- `code/rag/build_index.py`
- `code/rag/source_manifest_loader.py`
- `code/rag/bazi_rag_engine.py`

## 改动范围

- 新增 `code/knowledge/scripts/reconcile_01_sources.py`
- 输出对账 JSON: `report/八字判盘最强方案/reconcile_01.json`

## 核心实现

### 三方对账结果

| 来源 | 数量 |
|------|------|
| 磁盘 `数据库/01八字命理` | 143 |
| bazi_sources_manifest.json | 143 |
| index_report 01八字命理 | 143 文件 / 12354 chunks |

- onlyOnDisk: 0
- onlyInManifest: 0
- aligned: true

### 分层统计(manifest)

| authorityTier | 数量 | libraryRole | 数量 |
|---------------|------|-------------|------|
| S | 10 | judge_library | 62 |
| A | 13 | experience_library | 62 |
| B | 39 | supplement_library | 19 |
| C | 62 | | |
| D | 19 | | |

### metadata 字段

`build_index.py` 已为每个 chunk 写入: authorityTier, evidenceRole, libraryRole, canJudge, classic, sourceFile 等; `bazi_rag_engine.py` 支持 authority_tiers/evidence_roles/library_roles/judge_only 过滤与 evidenceBucket 分区喵

## 真实数据处理

- 对账命令: `python code/knowledge/scripts/reconcile_01_sources.py --output report/八字判盘最强方案/reconcile_01.json`
- 重建命令: `python code/rag/build_index.py --category 01`
- 重建在本环境因 Chroma/posthog TypedDict 兼容错误未成功执行; 既有索引已与 manifest 143 文件对齐, 可继续使用

## 验证命令

```bash
python code/knowledge/scripts/reconcile_01_sources.py
python code/rag/build_index.py --category 01
```

## 验证结果

- 对账: aligned=true, exit 0
- 索引重建: 失败(环境依赖), 但 index_report 显示 143/12354 与 manifest 一致
- 代码层 metadata 过滤与分区: `tests/test_classic_first_rag.py` 通过

## 偏差与风险

- 本机未能完成 Chroma 全量 reset 重建; 若 metadata 字段为近期新增, 建议在 Python 3.11+ 干净环境重跑 build_index
- 命例(C级)仍 enter RAG 但 canJudge=false, 检索须配合 judge_only 与 evidenceRole 过滤

## 下一阶段建议

进入阶段02: 从子平/滴天髓/渊海/三命通会抽取 geju/qishi/shishen/suiyun 第一批规则节点并 compile_graph喵

## 状态结论

**部分完成**. 对账与 metadata 代码验收完成; 索引物理重建受环境阻塞. Composer 2.5 按阶段 PLAN 实施, 未将大赛题纳入生产索引喵
