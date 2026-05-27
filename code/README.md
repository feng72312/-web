# 八字排盘 Web 平台 (MVP)

模块化八字算命 Web 应用, 便于后续扩展典籍资料、分析模块和 AI 解读.

## 目录结构

```
code/
  backend/          FastAPI 后端
    app/
      core/
        paipan/     排盘引擎 (确定性计算)
        analysis/   可注册分析模块
        rag/        可切换 RAG 提供者
        interpret/  解读编排
      api/          REST API
  frontend/         React + Vite 前端
    src/
      modules/      可注册 UI 区块
      registry/     前端模块注册表
```

## 扩展方式

### 后端新增分析模块

1. 在 `backend/app/core/analysis/modules/` 新建文件
2. 继承 `AnalysisModule`, 实现 `analyze()`
3. 在 `registry.py` 的 `build_default_registry()` 中 `register()`

### 前端新增展示模块

1. 在 `frontend/src/modules/` 新建组件
2. 在 `frontend/src/registry/sectionRegistry.ts` 中 `registerSectionModule()`

### 接入 RAG 知识库

设置环境变量:

```
BAZI_RAG_PROVIDER=http
BAZI_RAG_HTTP_URL=http://your-rag-bridge/search
```

当前默认为 `stub`, 待你接入 eyelevel-rag 桥接服务.

### 接入 Cursor SDK (Composer 2.5 AI 解读与对话)

1. 在 [Cursor Dashboard Integrations](https://cursor.com/dashboard/integrations) 创建 API Key
2. 复制 `backend/.env.example` 为 `backend/.env`, 填入:

```
BAZI_CURSOR_API_KEY=cursor_xxx
BAZI_CURSOR_MODEL=composer-2.5
```

3. 重启后端. 排盘后将使用 AI 生成命理解读, 并可在页面下方进行多轮追问.

相关 API:

- `GET /api/v1/chat/status` 检查 Cursor 是否已配置
- `POST /api/v1/chat/send` 非流式对话
- `POST /api/v1/chat/stream` SSE 流式对话

未配置 API Key 时, 解读区保持原有演示模式, 不影响排盘功能.

## 启动 (推荐)

**一键启动 (Windows):**

双击 `d:\ZY\code\start-all.bat`

会打开两个窗口: 后端 API + 前端页面.

- 前端: http://127.0.0.1:5173
- 后端文档: http://127.0.0.1:8000/docs

**分开启动:**

1. 双击 `start-backend.bat`
2. 双击 `start-frontend.bat` (会先 build 再 preview, 比 dev 模式更稳定)

### 手动启动

**后端:**

```powershell
cd d:\ZY\code\backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**前端:**

```powershell
cd d:\ZY\code\frontend
npm install --cache .npm-cache
npm run build
npm run preview
```

注意: 请用 `python -m uvicorn`, 不要直接用 `uvicorn` 命令 (可能不在 PATH 里).
前端当前用 `preview` 模式, 避免部分 Windows 环境下 `npm run dev` 的 esbuild 异常.

## API

- `GET /api/v1/health` 健康检查
- `GET /api/v1/modules` 已注册分析模块
- `POST /api/v1/paipan` 排盘
- `POST /api/v1/interpret` 排盘 + RAG 解读 (配置 Cursor 后为 AI 解读)
- `GET /api/v1/chat/status` Cursor AI 状态
- `POST /api/v1/chat/send` AI 对话 (非流式)
- `POST /api/v1/chat/stream` AI 对话 (SSE 流式)

## 排盘规则 (当前默认)

- 换月: 节气
- 子时: sect=2 (0 点换日)
- 大运: 顺逆按性别与年干阴阳

可通过环境变量 `BAZI_PAIPAN_SECT` 调整.
