# 阶段21-战冲和好补抽与val baseline复测记录

## 阶段目标

补抽三命通会 `sanming_zhan_chong_he` 节点; 重跑 val 20题判盘链 baseline, 对比 coverageRate 与新增 eventLiunianRate喵

## 本阶段变更

### 图谱补抽

- `extract_liunian_sanming.py` 改用「冲克太岁/日犯岁君/相克相冲」等真实段落关键词
- 新增节点 `liunian:sanming_zhan_chong_he`
- 重编: liunian 21 -> 22, nodeCount 273 -> 274

### keys_liunian

- `SANMING_LIUNIAN_TRIGGERS` 增加战冲类触发, 挂载 `sanming_zhan_chong_he`

### baseline 脚本增强

- `val_judgement_baseline_local.py` 输出:
  - `eventLiunianOk` / `eventLiunianRate`
  - `missingEvent:*` 分布

## 验证结果

| 验证项 | 阶段20后 | 阶段21 |
|--------|----------|--------|
| liunian 节点数 | 21 | 22 |
| nodeCount | 273 | 274 |
| val coverageRate (20题) | 1.0 | 1.0 |
| eventLiunianRate (20题) | (未测) | 1.0 (20/20) |
| caseOverreach | 20 | 20 |
| pytest liunian_sanming + suiyun_event | - | 9 passed |

报告文件: `val_judgement_baseline_phase21.json`

说明:
- coverageRate 维持 1.0, 主题 event liunian 全量命中
- caseOverreach=20 因离线 baseline 未开 RAG 但仍加载命例参考, 与历史 local baseline 一致, 非回归

## 路线衔接

- 阶段22候选: caseOverreach 治理 (无 RAG 时禁用 caseReference 或补 primaryEvidence)
- 阶段22候选: val baseline 带 `--rag` 复测 primaryEvidenceCount喵
