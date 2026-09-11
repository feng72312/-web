## 1. 清洗

- [x] 1.1 `code/backend/app/core/agent/ai_text.py`：增加 `strip_agent_protocol`；`sanitize_ai_text` 开头调用
- [x] 1.2 `code/backend/tests/test_ai_text.py`：双 MODE + 查找段保留「我是李耳」；正文「研究」不误删；页脚用例仍过

## 2. 编排与包装

- [x] 2.1 `chat_orchestrator.py`：Cursor `send_once` 清洗后再落库；`_stream_cursor` 对累计文本剥离后只 yield 增量
- [x] 2.2 `service.py` 的 `wrap_message` 与 `_wrap_cursor_message` 改追问句，去掉默认「请结合上文命盘资料」

## 3. 验收

- [x] 3.1 `PYTHONPATH=. .venv/bin/pytest tests/test_ai_text.py tests/test_persona_orchestrator.py -q` 通过
- [x] 3.2 重启后端后，老子「我是谁」流式与完成态均无 `[MODE:`
