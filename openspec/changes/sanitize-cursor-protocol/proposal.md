## Why

Composer 2.5 走 Cursor Agent，会带上账号个人习惯（如 RIPER-5 的 `[MODE: RESEARCH]`）和研究过程。名人对话问「我是谁」时用户看到协议字，不是人物口吻。账号规则无法从产品关掉，必须在出字前清掉。

## What Changes

- 清洗完整回复里的 `[MODE: …]` 行和文首「查找人物包 / 结合命盘」元研究段
- Cursor 流式只推清洗后的增量，落库也用清洗全文
- `wrap_message` 不再默认写「请结合上文命盘资料」，改为直接回答并禁止输出模式标记
- 不改 Cursor Key、不改个人 Cursor 规则、不把 Agent cwd 指回仓库

## Capabilities

### New Capabilities

- `agent-protocol-sanitize`: 协议标记与元研究段剥离、流式增量、包装句约束

### Modified Capabilities

<!-- openspec/specs/ 主 specs 为空，无既有 capability 需要 delta -->

## Impact

- 后端：`app/core/agent/ai_text.py`、`chat_orchestrator.py`、`service.py`、`tests/test_ai_text.py`
- 前端：无改动（SSE 已是清洗后文本）
- 运行时：DeepSeek 完整回复路径也会走同一清洗；不新增依赖
