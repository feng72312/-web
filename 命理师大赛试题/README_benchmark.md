# Contest8 八字选择题评测

数据来源: [BaziQA](https://github.com/ChenJiangxi/BaziQA) `contest8_*.json`，与 `历年全球命理师大赛试题与答案整理.md` 一致。

## 数据划分

| 划分 | 年份 | 题数 |
|------|------|------|
| train | 2021-2023 | 120 |
| val | 2024 | 40 |
| test | 2025 | 40 |

JSON 文件目录: `命理师大赛试题/data/`

## 使用步骤

在 `code/backend` 配置 `.env` 中的 `BAZI_DEEPSEEK_API_KEY` 或 `BAZI_CURSOR_API_KEY`。

```powershell
cd d:\ZY\code\backend

# 1. 从训练集生成 few-shot 范例
python scripts/build_contest_fewshot.py

# 2. 在验证集上调参对比 (baseline vs few-shot)
python scripts/tune_contest_prompt.py

# 3. 在测试集上最终评测 (勿反复调参)
python scripts/run_contest_benchmark.py --split test --fewshot

# 快速试跑 (仅 5 题)
python scripts/run_contest_benchmark.py --split val --limit 5
```

报告输出: `code/backend/data/reports/`

## 命例讲解 (RAG)

`数据库/01八字命理` 下有大量 **实战命例**、**滴天髓命例**、**曲炜命例** 等讲解文档 (sources 索引里约 68+ 个命例相关文件).
评测默认会通过 `contest8_rag.py` 按题目主题检索 top5 片段并注入提示词.

**必须先启动 RAG 服务**, 否则命例检索为空:

```powershell
cd d:\ZY\code\rag
# 若尚未建索引: python build_index.py
.\start-rag.bat
```

复测时加上 few-shot (与上次完整评测一致):

```powershell
cd d:\ZY\code\backend
python scripts/run_contest_benchmark.py --split val --fewshot
```

关闭命例 RAG 做对照: `--no-case-rag`

## 说明

本流程为 **提示词 + 命盘结构化 + 知识图谱 + 命例RAG** 的评测与优化, 不是权重微调.
结构化知识图谱 (`code/knowledge/data/graph`) 目前以调候/干支为主, **命例内容主要在 RAG 向量库**.
