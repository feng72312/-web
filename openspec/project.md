# 项目上下文

## 项目目标

八字 (Bazi) 排盘与解读 Web 平台, 集成知识图谱、RAG 典籍检索、大赛 MCQ 基准评测 (Contest8 / 全球命理师大赛 2021-2025 共 200 题), 以及紫微、六爻等扩展通道。线上部署基于腾讯云 CloudBase (静态托管 + 云托管 API)。

## 技术栈

- 后端: Python 3.10, FastAPI, `PaipanEngine`, `BaziJudgementChain`
- 前端: React + Vite
- RAG: Chroma, 本地 `code/rag` 服务 (默认 8100 端口)
- LLM: DeepSeek API (`BAZI_DEEPSEEK_API_KEY`)
- 知识图谱: `code/knowledge/data`
- 评测: `code/backend/app/benchmark/contest8_*.py`, 报告在 `code/backend/data/reports/` 与 `report/命理师大赛/`

## 项目约定

### 代码风格

- Python 遵循现有模块划分: `core/paipan`, `core/judgement`, `core/knowledge`, `benchmark`
- 大赛 prompt 与路由逻辑集中在 `prompts_contest.py`, `contest_channel_route.py`
- 最小化 diff, 匹配周边命名与类型注解习惯

### 架构模式

- 排盘: `PaipanEngine` + `AnalysisRegistry` 产出 chart payload
- 判盘链: `BaziJudgementChain` 多 Judge 仲裁 + 分层证据 (典籍优先, 命例为辅)
- 大赛评测: `predict_one` 按通道决定是否跑判盘链、命例 RAG、结构化推理

### 测试策略

- 路由与 prompt 开关: `tests/test_contest_channel_route.py`, `tests/test_mcq_reasoning_mode.py`
- 判盘链: `tests/test_bazi_judgement_chain.py`, `tests/test_rule_graph_judges.py`
- LLM 评测: 子集先行, val 40 冒烟, 全量 200 在阶段边界跑

### Git 工作流

- 功能分支开发; 仅用户明确要求时提交
- OpenSpec 变更在 `openspec/changes/<change-id>/`, 完成后 archive 到 `openspec/changes/archive/`

## 领域上下文

- Contest8 题为四选一 MCQ, 按 `infer_question_theme` 分为婚姻感情、流年事件、学历等约 11 类
- 「应期」指涉及公历年份、虚龄、大运、择年选项的题干; 「静态」指本命格局/六亲/学历类无明确年份题
- 准确率基线 (2026-06-15): 全量 63/200; 目标 >= 69/200

## 重要约束

- 禁止使用模拟设备或模拟评测数据
- 感情/健康题型保持 full 判盘链; 应期/静态题型走独立通道 (见 `improve-contest-accuracy-by-theme` 变更)
- RAG 评测前须确认 8100 服务可用

## 外部依赖

- DeepSeek API
- 本地 RAG (`code/rag/start-rag.bat`)
- 腾讯云 CloudBase (可选, 部署用)
- 大赛题库: `命理师大赛试题/`, JSON 在 `命理师大赛试题/data/`
