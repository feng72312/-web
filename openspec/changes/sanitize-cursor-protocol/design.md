## Context

Composer 走 `AsyncAgent`。账号 RIPER 习惯会进生成。`sanitize_ai_text` 只剥页脚。Cursor `send_once` / `_stream_cursor` 不清洗，流式原样推 chunk。`wrap_message` 固定写「请结合上文命盘资料」，名人对话也会被当成调研任务。

## Goals / Non-Goals

**Goals:**

- 完整回复与 Cursor 流式都不出现 `[MODE: …]` 和文首元研究段
- 人物正文（如「我是李耳」）保留
- 包装句不再默认点「命盘资料」

**Non-Goals:**

- 关闭或改写用户 Cursor 规则
- 前端再做一层剥离
- 改 DeepSeek 模型 id 或人物包正文

## Decisions

1. **产品侧清洗，不赌 SDK 能关账号规则**  
   `setting_sources` 已空，协议字仍会出。清洗是唯一可控层。  
   备选：改个人规则。那是开发机习惯，不能当产品依赖。

2. **`strip_agent_protocol` 先于页脚剥离**  
   删整行 `[MODE: NAME]`；从文首连续去掉同时提到「结合上文命盘」或「人物包 / 相关资料里查找」的段。正文里单独出现「研究」不删。空结果保持空。  
   备选：只删 MODE 行。查找段仍会漏给用户。

3. **流式对累计文本剥离，只 yield 相对上次清洗结果的增量**  
   页脚剥离仍等全文结束，避免中途 `---` 误剪。落库用清洗全文。  
   备选：前端滤。气泡仍会闪协议字。

4. **包装句统一为直接回答**  
   `wrap_message` 与 `_wrap_cursor_message` 追问句：直接回答；禁止模式标记、研究过程、系统说明；有上文则结合，无则按当前设定；不重复开场白。

## Risks / Trade-offs

- [误删含「研究」的正文] → 只剥文首且需命中协议短语
- [流式首包全是协议字] → 该轮不 yield，等有可见正文
- [账号规则再变花样] → 清洗按已知模式；新花样另开 change

## Migration Plan

1. 部署并重启后端。
2. 名人对话老子问「我是谁」，流式与完成态都无 `[MODE:`。
3. 回滚：还原本 change 三文件即可。

## Open Questions

- 无。账号规则无法从产品关掉，已定为清洗。
