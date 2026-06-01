# Val 2024 对比: 无命例RAG vs 有命例RAG

| 配置 | 正确/总数 | 准确率 | 报告 |
|------|-----------|--------|------|
| few-shot only (上次) | 12/40 | 30.0% | contest8_val_full.json |
| few-shot + 命例RAG (本次) | 12/40 | 30.0% | contest8_val_case_rag_full.json |

配置说明: DeepSeek deepseek-chat、结构化命盘、知识图谱、8条 train few-shot.
本次每题额外检索知识库命例讲解 top5 (RAG 已启动).

## 对错变化 (7 题变好, 7 题变差)

**命例RAG 答对、上次答错 (7):**
- guangdong_female_19800824_P001-Q1
- female_19831028_P004-Q16
- male_19710412_P005-Q25
- female_19830326_P006-Q28
- female_19830326_P006-Q30
- female_19800921_P007-Q31
- female_19800921_P007-Q34

**命例RAG 答错、上次答对 (7):**
- chaozhou_male_19720108_P002-Q6
- chaozhou_male_19720108_P002-Q9
- male_19611230_P003-Q13
- male_19611230_P003-Q15
- female_19831028_P004-Q18
- male_19710412_P005-Q21
- female_19830326_P006-Q29

**两次都错:** 21 题

## 结论

总准确率相同, 但部分题目对错互换.
命例RAG 已接通, 尚未带来整体提升, 可能原因:
- 检索片段与当前命主四柱相似度不够
- top5 片段过长/噪声, 干扰四选一判断
- 需提高 topK 或按日柱/主题二次过滤

错题列表: contest8_val_case_rag_wrong.md (28题)
