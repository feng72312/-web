## Context

解读与对话经 `ChatOrchestrator.resolve_model` 分流。DeepSeek 走 `DeepSeekClient` 的 OpenAI Chat Completions。Cursor 分支仍在编排器里（`_send_cursor_*`、`interpret`），但 `CursorAgentService` 是空壳，`main.py` 传入 `cursor=None`。`requirements.txt` 已有 `cursor-sdk`。`.env` 已有 `BAZI_CURSOR_API_KEY` 与 `BAZI_CURSOR_MODEL=composer-2.5`。

前端多数页面 `useState("deepseek-chat")`，加载 `/chat/status` 后改成 `status.model`。改 `default_model()` 即可把默认切到 Composer，不必逐页改死值。

Python SDK 在服务端必须用 `AsyncClient.launch_bridge` + `AsyncAgent`。桥是本机 sidecar（`cursor-sdk-bridge`）。每次请求起桥是秒级冷启动；lifespan 持有一个 client 则只付一次启动，之后本机 HTTP 跳几十毫秒。Agent 本身（create / 可能的工具轮）仍比 DeepSeek 直连慢，这是产品取舍，不是桥能消掉的。

## Goals / Non-Goals

**Goals:**

- Composer 2.5 可作为解读与对话的一档模型，Key 有效时为默认
- 桥随后端常驻，一次启动、随 lifespan 关闭
- 展示名「大师B」，DeepSeek 三档仍可选
- 隔离工作区，Agent 不能改 ZY 源码
- 标准价，不用 Fast
- 流式只出文本，对齐现有 SSE `delta`

**Non-Goals:**

- Grok 或其他厂商
- 改 DeepSeek 的 chat/reasoner 到 v4-flash 正式 id（可另开 change）
- 把 Composer 当编码 Agent 用（不给 MCP、不指向仓库）
- systemd 级独立桥服务（本阶段跟后端进程走）
- 云端 Cloud Agent / 克隆仓库

## Decisions

1. **常驻桥挂在后端 lifespan，不做成独立 daemon**  
   后端本就常开。`async with await AsyncClient.launch_bridge(workspace=isolated_dir)` 包住应用寿命，或等价地在 startup 启动、shutdown `aclose`。  
   备选：独立 `cursor-sdk-bridge` + `AsyncClient.connect`。多一个要运维的进程，局域网脚本启动路径更碎。本阶段不选。

2. **local runtime + 隔离空目录**  
   `LocalAgentOptions(cwd=code/backend/data/composer-workspace)`。目录只放 `.gitkeep`，加入 `.gitignore` 忽略 store 产物。`setting_sources` 保持空，不加载 Cursor 用户/项目设置。  
   备选：cloud。要等虚机和克隆，解读更慢。  
   备选：`cwd=ZY`。Composer 可能改代码，不可接受。

3. **每个聊天会话一个 Agent，跟现有 `session_store._cursor_agents` 对齐**  
   `create_session` → `AsyncAgent.create`；追问 `resume` 或持有 handle。进程重启后内存 map 丢了，用 `AsyncAgent.resume` + 桥磁盘 store 尽量续上；续不上就新建（用户会丢轮次，与当前 DeepSeek 内存会话一致）。  
   备选：每次解读 `Agent.prompt` 一次性。多轮对话丢上下文，且每次都 create 更慢。

4. **关闭 Fast**  
   `model` 只传 `composer-2.5`，不传 `params: [{id: "fast", value: "true"}]`。文档写 Fast 是 IDE 默认，SDK 必须显式才开。实现时用 `Cursor.models.list()` 确认参数名，测试断言请求未带 fast。

5. **默认模型**  
   `default_model(cursor_enabled, deepseek_enabled)`：Cursor 开 → `composer-2.5`；只 DeepSeek → `deepseek-chat`。`CHAT_MODELS` 增加  
   `ChatModel("composer-2.5", "Composer 2.5", "Agent", "cursor", "大师B", 2)`。  
   配额 `TIER_FREE_DAILY_LIMITS` / `TIER_FREE_ORDER` 增加「大师B」（9999）。未知 id 仍回落「小师傅」。

6. **文本流式**  
   `send_stream` 只 yield assistant 文本块（`run.iter_text()` 或过滤 `type=="assistant"` 的 text）。工具/系统事件不进 SSE。`wait()` 必须调用。失败映射为现有 `AgentRunError`。

7. **Key 缺失**  
   `cursor_api_key` 空：不启动桥，`cursor=None`，行为与现在 DeepSeek-only 相同。不因为默认改成 Composer 而让整站 AI 不可用。

## Risks / Trade-offs

- [首字仍慢于 DeepSeek] → 常驻桥只去掉桥冷启动；产品文案不承诺更快。标准档可能比 Fast 更慢，用钱换稳定账单。
- [本机 Agent 乱改文件] → 隔离空 cwd，无 MCP，无 setting sources。
- [桥子进程泄漏] → lifespan 必须 shutdown；异常退出靠脚本重启后端回收。
- [cursor-sdk 版本漂移] → 锁已装版本的 create/stream API，单测用 fake service，不在 CI 打真网。
- [Cursor 账单] → 默认走 Composer 后用量从 DeepSeek 转到 Cursor；LAN 额度仍是次数不是美元。
- [内存会话与桥 store 不一致] → resume 失败则新建 Agent，不阻塞解读。

## Migration Plan

1. venv 确认 `cursor-sdk` 与 `cursor-sdk-bridge` 可执行。
2. 部署后重启后端；日志应有桥 ready，`/chat/status` 的 `model` 为 `composer-2.5` 且 `cursorEnabled=true`。
3. 回滚：清空或注释 `BAZI_CURSOR_API_KEY` 并重启，即回 DeepSeek-only；或 `git revert` 本 change。

## Open Questions

- Cursor 套餐并发是否够局域网多人同时解读（先按单人演示假设）。
- `iter_text()` 是否会把思维/内部独白也流出来，需接上后看一条真实解读再决定要不要再滤一层。
