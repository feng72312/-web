## 1. 模型目录与配额

- [x] 1.1 `code/backend/app/core/agent/models.py`：`CHAT_MODELS` 增加 `composer-2.5` / provider `cursor` / tier `大师B` / tier_rank 2；`default_model` 在 `cursor_enabled` 时返回 `composer-2.5`，否则 `deepseek-chat`
- [x] 1.2 `code/backend/app/core/quota/keys.py`：`TIER_FREE_DAILY_LIMITS` 与 `TIER_FREE_ORDER` 增加 `大师B`（9999）
- [x] 1.3 `code/frontend/src/utils/modelTier.ts`：`MODEL_DISPLAY_ORDER` 把 `composer-2.5` 放在最前；`MODEL_TIER_BY_ID` 映射为 `大师B`；`tierClassName` 将 `大师B` 归为 `master`

## 2. 常驻桥与 Cursor 服务

- [x] 2.1 确认 `code/backend/.venv` 已安装 `cursor-sdk` 且 `cursor-sdk-bridge` 在 PATH；缺则 `uv pip install`
- [x] 2.2 `code/backend/app/config.py`：增加 `cursor_workspace` 默认 `data/composer-workspace`（相对 backend 根，解析方式与 quota db 一致）
- [x] 2.3 新建隔离目录 `code/backend/data/composer-workspace/.gitkeep`；`.gitignore` 忽略该目录下除 `.gitkeep` 外的 store 产物
- [x] 2.4 重写 `code/backend/app/core/agent/service.py`：`enabled` 在有 key 时为真；startup 里 `AsyncClient.launch_bridge(workspace=isolated)` 并保存 client；shutdown 关闭 client；`create_session` / `send_once` / `send_stream` / `interpret` 用 `AsyncAgent` + `composer-2.5`、不传 Fast、无 MCP、空 setting sources；流式只出 assistant 文本并 `wait()`
- [x] 2.5 `code/backend/app/main.py` lifespan：有 key 则 `init_agent_service` + `startup`，`init_chat_orchestrator(cursor=service, ...)`；shutdown 调 `service.shutdown`

## 3. 编排与测试

- [x] 3.1 保持 `chat_orchestrator.py` 的 cursor 分流；确认 `resolve_model` 能命中 `composer-2.5` 且不再把未知 cursor 请求静默打到 DeepSeek
- [x] 3.2 `tests/test_persona_orchestrator.py` 与新增 `tests/test_composer_default.py`：默认模型、list_models 含/不含 composer、无 key 不启桥、`tier_for_model("composer-2.5")=="大师B"`、配额扣 `大师B`
- [x] 3.3 Fake `CursorAgentService` 覆盖 `send_once` / `send_stream` 文本过滤（工具事件不进入 yield）
- [x] 3.4 `pytest tests/test_persona_orchestrator.py tests/test_composer_default.py tests/test_quota.py tests/test_admin.py -q` 通过

## 4. 验收

- [x] 4.1 重启后端；`curl /api/v1/chat/status` 在 Key 有效时 `cursorEnabled=true`、`model=composer-2.5`、models 含大师B
- [x] 4.2 `pgrep -a cursor-sdk-bridge` 在后端运行期间恰有 1 个；连续两次解读后仍是 1 个
- [x] 4.3 浏览器打开模块页，选择器默认大师B；走一遍八字流式解读，有 delta 文本；再选手动切小师傅确认 DeepSeek 仍可用
- [x] 4.4 停后端后 `cursor-sdk-bridge` 不残留
