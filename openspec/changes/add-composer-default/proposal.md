## Why

局域网解读现在只走 DeepSeek。用户要启用 Composer 2.5 作为默认大师档（展示名「大师B」），DeepSeek 三档保留可选。Cursor Agent 服务此前被掏空，必须重新接上 SDK，并用常驻桥去掉每次冷启动。

## What Changes

- 恢复 `CursorAgentService`：用 Python `cursor-sdk` 的 `AsyncClient` + `AsyncAgent` 跑 `composer-2.5`
- 后端 lifespan 启动时拉起并持有 `cursor-sdk-bridge`，关闭时释放；禁止每次解读新建桥
- Agent 工作区用隔离空目录，禁止以 ZY 仓库为 `cwd`，避免编码 Agent 改项目文件
- 明确关闭 Composer Fast 档（标准价 $0.50/$2.50，不用默认 Fast $3/$15）
- 模型目录加入 `composer-2.5`，展示名「大师B」；`/chat/status` 的默认 `model` 在 Cursor 可用时为 `composer-2.5`
- 前端选择器与配额认「大师B」；各页 `selectedModel` 跟随 `status.model`
- DeepSeek 小师傅 / 大师 / 资深道长仍可选；Cursor Key 缺失时回退 DeepSeek，不空窗
- 流式只转发 assistant 文本块，过滤工具事件；失败走现有 `error` / 非流式回退

## Capabilities

### New Capabilities

- `composer-agent-provider`: Cursor Agent SDK 接入、常驻桥生命周期、隔离工作区、标准档、文本流式与会话绑定
- `chat-model-defaults`: 模型目录、默认模型、展示名「大师B」、配额键与前端跟随 `/chat/status`

### Modified Capabilities

<!-- openspec/specs/ 主 specs 为空，无既有 capability 需要 delta -->

## Impact

- 后端：`app/core/agent/service.py`、`models.py`、`chat_orchestrator.py`、`main.py` lifespan、`config.py`、`quota/keys.py`、`tests/`（cursor 编排、默认模型、配额）
- 前端：`utils/modelTier.ts`；各 Tab / 工具页初始值可仍为占位，以 `status.model` 为准
- 依赖：`cursor-sdk` 已在 `requirements.txt`；需确认 venv 已安装且能启动 `cursor-sdk-bridge`
- 运行时：后端进程多一个常驻桥子进程与本机 agent store；Cursor 用量记 Cursor 套餐，不记 DeepSeek
- 密钥：继续用 `BAZI_CURSOR_API_KEY`，不提交 `.env`
