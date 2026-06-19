# 阶段23-contest错因标注与tieredEvidence分组说明记录

## 阶段目标

contest 答错时优先用 coverage.caseOverreach 标 case_overfit; API/判盘链返回 tieredEvidence 分层说明; 前端判盘面板展示分层证据摘要喵

## 本阶段变更

### error_labels

- `infer_error_labels` 优先读取 `judgement.coverage.caseOverreach`
- 补充规则: 有 case 无 primary 也标 case_overfit

### evidence / chain / models

- 新增 `build_tiered_evidence_summary(tiered)`:
  - groups: 主裁/辅助/命例/低信 计数与 preview
  - caseOverreachRisk / note
- `BaziJudgementReport.tieredEvidenceSummary` 随 chain.run 自动填充

### API

- `JudgementResponse` 新增 `tieredEvidenceSummary`
- `/paipan/judgement` 与 `/paipan/interpret` 均返回该字段

### 前端

- `BaziJudgementReport` / `Interpretation` 类型扩展
- `BaziJudgementPanel` 展示分层证据区与越权风险提示

### 测试

- 更新 `test_contest_error_labels.py`
- 新建 `test_tiered_evidence_summary.py`

## 验证结果

| 验证项 | 结果 |
|--------|------|
| pytest error_labels + tiered_summary + offline coverage | 见本机执行 |
| contest 全量重跑 | 用户要求跳过 |

## 路线衔接

- 阶段24候选: contest regression 报告输出 error_labels 分布 (无需 LLM 全量)
- 阶段24候选: 部署后 smoke `/paipan/judgement` 检查 tieredEvidenceSummary喵
