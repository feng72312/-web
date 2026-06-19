# 阶段24-paipan/judgement API smoke 记录

## 目标

跳过做题评测, 对 `POST /api/v1/paipan/judgement` 做 HTTP smoke, 验证 `tieredEvidenceSummary` 字段喵

## 新增脚本

- `code/backend/scripts/smoke_judgement_api.py`
  - `--base` 指定 API 根地址
  - 校验 top-level 与 judgement 内嵌 tieredEvidenceSummary
  - 校验 opinionCount >= 5 且 summary total > 0

## 本地 smoke (127.0.0.1:8000)

| 项 | 结果 |
|----|------|
| HTTP 状态 | 200 ok |
| dayMaster | 己 |
| topTieredSummaryTotal | 5 |
| nestedTieredSummaryTotal | 5 |
| topGroups | 主裁证据, 命例参考 |
| caseOverreachRisk | false |
| primaryEvidenceCount | 3 |
| caseReferenceCount | 2 |
| opinionCount | 6 |
| note | 命例仅作参考, 不得单独决定格局与用神 |

报告: `smoke_judgement_api_local.json`

结论: **本地 API smoke 通过**

## 线上 smoke (CloudRun bazi-api)

| 项 | 结果 |
|----|------|
| /health | 200 |
| /api/v1/paipan/judgement | **404 Not Found** |
| openapi judgement 路径 | 无 |

结论: 线上容器尚未包含 `/paipan/judgement` 与 `tieredEvidenceSummary`, 需后端部署后复测

报告: `smoke_judgement_api_prod.json` (失败记录)

## 下一步 (需你确认再部署)

仅后端变更, 可走 bazi-deploy skill 步骤 2+4+6+7 发布 bazi-api, 再重跑:

```powershell
py -3.10 scripts/smoke_judgement_api.py --base https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com
```

喵
