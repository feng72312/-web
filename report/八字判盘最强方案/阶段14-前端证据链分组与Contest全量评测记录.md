# 阶段14-前端证据链分组与Contest全量评测记录

## 阶段目标

前端证据链按格局分组展示, 与后端 geju 分组 evidenceChain 对齐; 跑通 DeepSeek contest val 全量 40 题准确率回归喵

## 本阶段变更

### 前端证据链分组

- `BaziJudgementPanel.tsx` 识别结论前缀 `月令格局/成败救应/杂格外格/其他`
- 子平真诠格局证据单独分区展示, 含 ruleIds 与原文 quote
- 其余裁判证据保持平铺列表
- `bazi-visual-demo.css` 增加 `.bazi-evidence-geju-groups` 样式

### Contest 评测

- 修复 `run_contest_benchmark.py` 缺失 `--ziwei-only` 参数 (阶段13已修)
- 跑通 val 全量 40 题: `contest8_val_geju_special_full.json`
- 生成错因回归: `contest8_val_geju_special_regression.json`

## 验证结果

### Contest val 准确率对比

| 报告 | 准确率 | 正确数 |
|------|--------|--------|
| geju_special_full (本阶段) | 35.0% | 14/40 |
| bazi_kg (知识图谱基线) | 32.5% | 13/40 |
| val_full / baseline | 30.0% | 12/40 |

本阶段较 bazi_kg 基线 **+2.5%** (多对 1 题), 较 30% 基线 **+5%**喵

### 错因分布 (错题)

| 错因标签 | 次数 |
|----------|------|
| overconfident_claim | 26 |
| wrong_tiaohou | 15 |
| wrong_liunian | 14 |
| case_overfit | 7 |
| wrong_yongshen | 5 |

主瓶颈仍在调候与流年, 格局增厚未引入 case_overreach 类退化喵

### 其他

- RAG + 知识图谱 + 判盘链 contest 流程全量跑通 (~33 分钟)
- smoke 5 题 20% 不代表全量, 全量 35% 更可信

## 输出文件

- `code/backend/data/reports/contest8_val_geju_special_full.json`
- `report/八字判盘最强方案/contest8_val_geju_special_full.json`
- `report/八字判盘最强方案/contest8_val_geju_special_regression.json`

## 仍待深化

1. contest 结果中 judgement 字段未完整回写, coverageOk 统计为 0, 需 eval 管线嵌入 BaziJudgementChain 输出
2. 调候/流年错因仍最高, 下一步应优先《穷通宝鉴》调候链与流年专题
3. 从格真/假从精细触发尚未做
4. test split 40 题全量回归待跑

## 状态结论

**完成**. 前端证据链格局分组已接通, contest val 全量 35% 略优于知识图谱基线 32.5%, 未出现准确率退化喵
