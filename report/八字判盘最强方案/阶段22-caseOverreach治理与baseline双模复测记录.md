# 阶段22-caseOverreach治理与baseline双模复测记录

## 阶段目标

修复离线判盘链 caseOverreach=20/20: 无 RAG 时不加载命例参考, 用图谱 ruleIds 填充 primaryEvidence; 复测 local 与 --rag 两套 baseline喵

## 本阶段变更

### evidence.py

- 新增 `build_graph_primary_evidence(verdicts)`: 将裁判 ruleIds 解析为 primaryEvidence (libraryRole=rule_graph)

### chain.py

- `use_rag=False` 时:
  - 跳过 `load_case_references`
  - `tiered.primaryEvidence` 来自图谱 ruleIds
  - 不再写入 caseReference
- `use_rag=True` 时: 行为不变 (RAG primary + caseReference 附录)

### 测试

- 新建 `tests/test_judgement_coverage_offline.py`

## 验证结果

| 验证项 | 阶段21 | 阶段22 local | 阶段22 --rag |
|--------|--------|--------------|--------------|
| coverageRate | 1.0 | 1.0 | 1.0 |
| eventLiunianRate | 1.0 | 1.0 | 1.0 |
| caseOverreach | 20 | **0** | **0** |
| primaryEvidenceCount (典型题) | 0 | 16 | >0 (RAG+图谱) |
| caseReferenceCount | 2 | 0 | 仍有 case 附录 |
| pytest offline coverage | - | 5 passed | - |

报告:
- `val_judgement_baseline_phase22.json` (local)
- `val_judgement_baseline_phase22_rag.json` (RAG, 端口8100)

## 路线衔接

- 阶段23候选: contest eval 接入 caseOverreach 硬约束 (答错时优先标 case_overfit)
- 阶段23候选: API `/judgement` 返回 tieredEvidence 分组说明喵
