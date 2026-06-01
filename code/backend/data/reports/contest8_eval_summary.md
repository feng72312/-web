# Contest8 完整评测汇总

评测时间: 2026-05-28  
配置: DeepSeek `deepseek-chat` + 结构化命盘 + 知识图谱 + train few-shot(8条)  
原始报告: `contest8_val_full.json`, `contest8_test_full.json`

## 准确率

| 划分 | 年份 | 正确/总数 | 准确率 |
|------|------|-----------|--------|
| val | 2024 | 12/40 | **30.0%** |
| test | 2025 | 13/40 | **32.5%** |

随机猜题基线约 25%。当前略高于随机，仍远低于专业命理师大赛水平。

## 错题明细文件

- val 28 题: [contest8_val_full_wrong.md](contest8_val_full_wrong.md)
- test 27 题: [contest8_test_full_wrong.md](contest8_test_full_wrong.md)

## 错题主题粗分 (val+test)

| 主题 | 约错题数 | 说明 |
|------|----------|------|
| 婚姻/感情/子女 | 18+ | 配偶星、合冲、流年引动难对齐 |
| 职业/财运/学历 | 14+ | 财官食伤与大运对应不稳 |
| 健康/意外/流年事件 | 12+ | 具体年份与事件类型易混 |
| 性格/外貌/家庭背景 | 10+ | 描述性选项区分度低 |

## 后续建议

1. 启动 RAG (`code/rag/start-rag.bat`) 再复测  
2. 增大或按题型筛选 few-shot  
3. 对婚姻/流年类题增加专项推理步骤
