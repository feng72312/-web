# 阶段20-三命通会流年扩充与event覆盖校验记录

## 阶段目标

从《三命通会》抽取 liunian 专题节点并入图谱; SuiYunJudge 按题干关键词挂载 sanming_* 规则; baseline coverage 校验 event liunian 是否覆盖喵

## 本阶段变更

### 图谱扩充

- 新建 `code/knowledge/scripts/extract_liunian_sanming.py`
- 产出 `data/draft/liunian_sanming.draft.jsonl` (6节点)
  - sanming_zhen_taisui / sanming_suiyun_binglin / sanming_taisui_head
  - sanming_fuyin / sanming_fanyin / sanming_xiaoyun
- `compile_graph.py` 重编: liunian 15 -> 21, nodeCount 267 -> 273

### keys_liunian

- 新增 `resolve_sanming_liunian_categories(question)`
- `select_liunian_categories` 在并临/真太岁/伏吟/小运等关键词时追加 sanming_* category

### coverage 校验

- `enrich_question` 新增 `expectedEventLiunian`
- `check_judgement_coverage` 新增:
  - `missingEventLiunian`
  - `eventLiunianCovered`
  - `covered` 同时要求 event liunian 命中

### 证据链与前端

- 新增分组「三命流年」展示 `liunian:sanming_*`

### 测试

- 新建 `tests/test_liunian_sanming_coverage.py`

## 验证结果

| 验证项 | 结果 |
|--------|------|
| extract_liunian_sanming | 6 nodes |
| compile_graph | liunian=21, nodeCount=273 |
| pytest liunian_sanming_coverage + suiyun_event | 见本机执行 |
| contest 全量重跑 | 用户要求跳过 |

## 路线衔接

- 阶段21候选: sanming_zhan_chong_he 专题补抽 (战冲和好段落)
- 阶段21候选: val baseline 20题重跑 coverageRate 对比 (不重跑 contest LLM)喵
