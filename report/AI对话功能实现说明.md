# AI API接入交接说明

生成时间: 2026-06-15

## 1. 文档目的

本文面向接手同事, 说明在已经具备 AI API Key 的前提下, 当前项目如何接入 AI 能力、API Key 应配置在哪里、前端如何调用项目后端接口、后端如何转发到模型服务, 以及上线和联调时需要检查哪些事项。

当前项目不建议让前端直接调用模型厂商 API。正确接入方式是: 前端调用本项目后端 `/api/v1/chat/*` 接口, 后端读取 AI API Key, 再由后端请求 DeepSeek OpenAI-compatible Chat Completions API。

## 2. 当前接入结论

当前生产链路使用 DeepSeek 作为 AI 模型提供方。后端文件 `code/backend/app/main.py` 在应用启动时读取配置, 初始化 `DeepSeekClient`, 再交给 `ChatOrchestrator` 处理多轮对话。

需要给同事交接的核心点只有三个:

1. 把 AI API Key 配到后端环境变量 `BAZI_DEEPSEEK_API_KEY`。
2. 前端只调用项目后端 `API_BASE + /chat/*`, 不暴露模型 Key。
3. 聊天主流程先初始化会话拿 `agentId`, 再用 `agentId` 调用 `/chat/stream` 发送消息。

## 3. 服务端配置方法

### 3.1 必填配置

在后端运行环境中配置:

```env
BAZI_DEEPSEEK_API_KEY=你的DeepSeek_API_Key
```

本地开发时通常写入:

```text
code/backend/.env
```

云端部署时需要写入对应 CloudRun 或后端服务的环境变量, 不要写入前端构建产物, 也不要把真实 Key 提交到 Git。

### 3.2 可选配置

如果使用 DeepSeek 官方地址, 可以不配置 base url, 代码默认值是 `https://api.deepseek.com`。

如需切换到兼容 DeepSeek/OpenAI 格式的代理地址, 可以配置:

```env
BAZI_DEEPSEEK_BASE_URL=https://api.deepseek.com
```

后端实际请求地址会拼成:

```text
{BAZI_DEEPSEEK_BASE_URL}/v1/chat/completions
```

### 3.3 相关代码位置

| 作用 | 文件 |
| --- | --- |
| 环境变量定义 | `code/backend/app/config.py` |
| 应用启动时初始化 DeepSeek | `code/backend/app/main.py` |
| DeepSeek HTTP 客户端 | `code/backend/app/core/agent/deepseek.py` |
| 对话编排 | `code/backend/app/core/agent/chat_orchestrator.py` |

## 4. 前端 API Base 配置

前端不会直接读取 AI API Key, 只需要知道项目后端 API 地址。

配置逻辑在:

```text
code/frontend/src/services/config.ts
```

当前规则:

| 场景 | API Base |
| --- | --- |
| 本地 `localhost` 或 `127.0.0.1` | `/api/v1`, 通过 Vite proxy 转发到本地后端 |
| CloudBase 域名 | `https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1` |
| 其他环境 | 优先使用 `VITE_API_BASE`, 否则使用生产 API Base |

如果同事部署了新的后端地址, 前端构建时设置:

```env
VITE_API_BASE=https://你的后端域名/api/v1
```

## 5. 前端调用顺序

AI 对话不是直接发一句话给模型, 而是先创建项目内部会话, 再基于会话发送消息。

### 5.1 通用 AI 顾问

适合无命盘上下文的普通入口。

第一步, 初始化会话:

```http
POST /api/v1/chat/init/general
Content-Type: application/json
```

请求体:

```json
{
  "scenario": "general",
  "title": "AI顾问",
  "initialPrompt": "可选的初始问题"
}
```

响应:

```json
{
  "agentId": "会话ID",
  "title": "AI顾问",
  "scenario": "general"
}
```

第二步, 使用 `agentId` 调用流式聊天接口 `/chat/stream`。

### 5.2 八字或模块带上下文对话

适合已经有排盘结果, 希望 AI 基于当前盘继续解释。

初始化接口:

```http
POST /api/v1/chat/init
Content-Type: application/json
```

请求体:

```json
{
  "chart": {
    "这里放排盘结果": "..."
  },
  "sections": [
    {
      "这里放模块分析章节": "..."
    }
  ]
}
```

响应:

```json
{
  "agentId": "会话ID"
}
```

后端会基于 `chart` 和 `sections` 生成 system prompt, 并把知识库压缩上下文注入会话。这个接口只初始化上下文, 不消耗 AI 配额, 也不调用模型。

### 5.3 多模块融合对话

适合把八字、紫微、六爻等多个模块结果放到同一个 AI 对话里综合分析。

初始化接口:

```http
POST /api/v1/chat/init/fusion
Content-Type: application/json
```

请求体:

```json
{
  "title": "融合分析",
  "sources": [
    {
      "moduleId": "bazi",
      "moduleLabel": "八字",
      "title": "八字解读",
      "question": "用户原问题",
      "chartSnapshot": {},
      "summaryPlain": "白话摘要",
      "summaryProfessional": "专业摘要",
      "createdAt": "2026-06-15T00:00:00.000Z"
    },
    {
      "moduleId": "ziwei",
      "moduleLabel": "紫微",
      "title": "紫微解读",
      "chartSnapshot": {}
    }
  ]
}
```

限制: `sources` 最少 2 个, 最多 6 个。

响应:

```json
{
  "agentId": "会话ID",
  "title": "融合分析",
  "scenario": "review_result",
  "sourceCount": 2
}
```

## 6. 流式发送消息

当前前端主路径使用 SSE 流式接口:

```http
POST /api/v1/chat/stream
Content-Type: application/json
X-Device-Id: 设备ID
X-Model-Id: deepseek-chat
Authorization: Bearer 登录token, 可选
```

请求体:

```json
{
  "agentId": "初始化得到的会话ID",
  "message": "用户输入的问题",
  "model": "deepseek-chat"
}
```

字段说明:

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `agentId` | 是 | 由 `/chat/init*` 返回 |
| `message` | 是 | 用户消息, 长度 1 到 4000 |
| `model` | 否 | 不传时后端使用默认模型 |
| `X-Device-Id` | 是 | 匿名用户配额账户标识 |
| `Authorization` | 否 | 已登录用户的 CloudBase token |
| `X-Model-Id` | 否 | 用于后端按模型档位扣配额 |

SSE 返回格式:

```text
data: {"type":"delta","text":"第一段文本"}

data: {"type":"delta","text":"第二段文本"}

data: {"type":"done","runId":"deepseek-xxxxxxxx"}
```

错误时可能返回:

```text
data: {"type":"error","message":"错误信息"}
```

前端解析方式参考:

```text
code/frontend/src/services/chatApi.ts
```

核心逻辑是读取 `response.body.getReader()`, 按 `\n\n` 拆分 SSE event, 再解析每行以 `data:` 开头的内容。

## 7. 非流式发送消息

项目保留了非流式接口:

```http
POST /api/v1/chat/send
Content-Type: application/json
X-Device-Id: 设备ID
X-Model-Id: deepseek-chat
Authorization: Bearer 登录token, 可选
```

请求体:

```json
{
  "agentId": "初始化得到的会话ID",
  "message": "用户输入的问题",
  "model": "deepseek-chat"
}
```

响应:

```json
{
  "agentId": "会话ID",
  "runId": "deepseek-xxxxxxxx",
  "text": "完整回复文本"
}
```

说明: 当前正式 UI 主要使用 `/chat/stream`, `/chat/send` 更适合脚本、调试或不需要流式体验的客户端。

## 8. 模型档位

当前后端暴露的模型定义在:

```text
code/backend/app/core/agent/models.py
```

| modelId | 前端显示档位 | provider |
| --- | --- | --- |
| `deepseek-chat` | 小师傅 | deepseek |
| `deepseek-reasoner` | 大师 | deepseek |
| `deepseek-v4-pro` | 资深道长 | deepseek |

获取当前后端可用模型:

```http
GET /api/v1/chat/status
```

响应示例:

```json
{
  "enabled": true,
  "model": "deepseek-chat",
  "runtime": "",
  "models": [
    {
      "id": "deepseek-chat",
      "label": "小师傅",
      "tag": "Chat",
      "provider": "deepseek",
      "tier": "小师傅",
      "tierRank": 1
    }
  ],
  "cursorEnabled": false,
  "deepseekEnabled": true
}
```

## 9. 配额和鉴权

发送 AI 消息会扣配额, 初始化会话不扣配额。

后端识别账户的顺序:

1. 如果请求带 `Authorization: Bearer <token>` 且 CloudBase 鉴权成功, 使用登录用户 uid。
2. 如果未登录, 使用请求头 `X-Device-Id` 作为匿名设备账户。

前端生成请求头的代码在:

```text
code/frontend/src/services/deviceHeaders.ts
```

配额不足时后端返回 HTTP 402。前端应提示用户次数不足, 并刷新配额状态。

## 10. 后端到模型厂商的调用方式

后端 `DeepSeekClient` 使用 OpenAI-compatible Chat Completions 格式请求模型。

非流式请求核心结构:

```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "会话初始化时生成的系统提示词"
    },
    {
      "role": "user",
      "content": "用户问题"
    }
  ],
  "stream": false
}
```

流式请求核心结构:

```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "会话初始化时生成的系统提示词"
    },
    {
      "role": "user",
      "content": "用户问题"
    }
  ],
  "stream": true
}
```

请求头:

```http
Authorization: Bearer <BAZI_DEEPSEEK_API_KEY>
Content-Type: application/json
```

注意: 厂商 API Key 只存在于后端环境变量和后端请求头中, 不进入前端。

## 11. 前端最小接入示例

同事如果只想接一个最小聊天页, 可以按下面顺序做。

第一步, 初始化通用会话:

```ts
const initRes = await fetch(`${API_BASE}/chat/init/general`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ scenario: "general", title: "AI顾问" }),
});
const { agentId } = await initRes.json();
```

第二步, 发送流式消息:

```ts
const res = await fetch(`${API_BASE}/chat/stream`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-Device-Id": deviceId,
    "X-Model-Id": "deepseek-chat",
  },
  body: JSON.stringify({
    agentId,
    message: "帮我解释一下当前问题",
    model: "deepseek-chat",
  }),
});

const reader = res.body?.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (reader) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });
  const events = buffer.split("\n\n");
  buffer = events.pop() ?? "";

  for (const event of events) {
    const line = event.split("\n").find((item) => item.startsWith("data: "));
    if (!line) continue;
    const payload = JSON.parse(line.slice(6));
    if (payload.type === "delta") {
      console.log(payload.text);
    }
    if (payload.type === "done") {
      console.log("done", payload.runId);
    }
    if (payload.type === "error") {
      console.error(payload.message);
    }
  }
}
```

项目内已有封装:

```text
code/frontend/src/services/chatApi.ts
```

优先复用 `initGeneralChatSession`, `initChatSession`, `initFusionChatSession`, `streamChatMessage`。

## 12. 联调检查清单

交接同事联调时按下面顺序检查:

1. 后端环境变量已配置 `BAZI_DEEPSEEK_API_KEY`。
2. 后端已重启, 确保新环境变量生效。
3. 访问 `GET /api/v1/chat/status`, 确认 `enabled=true` 且 `deepseekEnabled=true`。
4. 前端 `API_BASE` 指向正确后端。
5. 请求 `/chat/stream` 时带 `X-Device-Id`。
6. 如果是登录用户, 请求带 `Authorization: Bearer <token>`。
7. 先调用 `/chat/init/general` 或 `/chat/init`, 再调用 `/chat/stream`。
8. SSE 解析时按空行 `\n\n` 拆分事件。
9. 如果返回 402, 先检查配额, 不是模型 Key 问题。
10. 如果返回 503, 优先检查模型 Key、base url、厂商服务状态和后端日志。

## 13. 常见错误

| 现象 | 可能原因 | 处理方式 |
| --- | --- | --- |
| `/chat/status` 返回 `enabled=false` | 后端没有读到 API Key | 配置 `BAZI_DEEPSEEK_API_KEY` 后重启后端 |
| `/chat/init*` 返回 404 | 后端旧进程或路由未加载 | 重启后端服务 |
| `/chat/stream` 返回 400 | 用户消息被范围守卫拒绝 | 调整问题到命理、术数、解读相关范围 |
| `/chat/stream` 返回 402 | AI 配额不足 | 刷新配额或兑换额度 |
| `/chat/stream` 返回 503 | 模型调用失败 | 检查 Key、base url、网络和后端日志 |
| 前端没有逐字输出 | 没有按 SSE 解析 | 按 `data: {...}\n\n` 事件格式解析 |

## 14. 交接给同事的一句话版本

这个项目的 AI 接入方式是后端代理模式: 把 DeepSeek API Key 配到后端 `BAZI_DEEPSEEK_API_KEY`, 前端先调用 `/api/v1/chat/init/general` 或 `/api/v1/chat/init` 拿 `agentId`, 再带 `X-Device-Id` 调 `/api/v1/chat/stream` 读取 SSE 增量文本。前端不要直接接触模型厂商 Key。
