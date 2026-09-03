## Why

ZY 已在局域网 Ubuntu 服务器上跑通（前端 5173 / 后端 8002 / RAG 8100，Cloudflare 临时隧道按需开启），但实测暴露出几类"投入小、收益大"的问题：主包未压缩 5.0MB 且单 chunk；模块 AI 解读全部非流式，用户对着转圈 30–70 秒；两个肉眼可见的显示 bug（五行条无填色、深色主题四柱表格白底）；CloudBase 遗留的额度提示与兑换入口对局域网用户只是噪音；RAG 在 Linux 上重排序关闭且 torch 为 CPU 版，旁边 RTX 4090 空闲；后端日志已出现 400+ 次公网 IP 访问，隧道一开 DeepSeek 账单即对全网开放，管理员密码还硬编码在 `config.py`。这些都不需要大改架构，适合作为一次集中修复。

## What Changes

- 前端构建开启 esbuild minify 与 modulePreload，按 vendor（react / antd / echarts / framer-motion / assistant-ui）拆 chunk，`ModulesPage` 的 10 个模块 Tab 改为 `React.lazy` 按需加载
- 八字 `/interpret/stream` 升级到与 `/interpret` 同等的完整载荷（判定链、分级证据、段落锚点、置信度），前端八字解读改走流式并在页面实时渲染增量文本；流式不可用时自动回退非流式。其余模块（塔罗、六爻、紫微等）沿用非流式，作为后续 change
- 修复 `.bazi-report-wuxing-fill` 无背景色；修复 `chart-detail.css` 中 `tr.detail-alt` 硬编码浅色背景导致深色主题四柱表格白底
- 移除 CloudBase 遗留 UI：`QuotaBar` 不再请求持久化状态、不再显示"服务端数据尚未持久化"提示与"兑换秘钥"面板；额度 9999 场景下配额条简化为静默（仍保留后端 quota 接口与 SQLite，便于将来恢复）
- RAG Linux 启动脚本默认 `RAG_RERANK=1`；RAG venv 安装 CUDA 版 torch；embedding 与 reranker 通过 `RAG_DEVICE` 环境变量选择设备，默认 `cuda` 可用则用 cuda 否则 cpu；`/health` 返回 `chunks`、`device`、`rerank` 字段，关闭 Chroma anonymized telemetry
- 隧道访问口令：后端新增中间件，当请求带 `CF-Connecting-IP`（即经 cloudflared 进入）且服务器存在口令文件时，对 AI 计费路由（`*/interpret*`、`/chat/*`、`/rag/search`）要求 `X-Access-Code` 头匹配，否则 401；局域网直连请求不受影响。`start-tunnel.sh` 生成/读取口令并写入口令文件，`stop-tunnel.sh` 删除口令文件。前端收到 401 access-code 错误时弹窗让用户输入口令，存 localStorage 并重试
- **BREAKING**（仅对管理端）：`admin_password` 不再有默认值，未在 `.env` 配置 `ADMIN_PASSWORD` 时管理接口一律 403

## Capabilities

### New Capabilities
- `frontend-bundle-optimization`: 生产构建的压缩、分包与模块级懒加载要求
- `bazi-interpret-streaming`: 八字解读 SSE 流式接口的事件协议、载荷完整性与前端回退行为
- `bazi-report-theming`: 八字报告视图五行分布条与四柱表格在亮/暗主题下的可见性要求
- `lan-quota-display`: 局域网无登录场景下配额条的展示与不再依赖 CloudBase 持久化探测
- `rag-gpu-rerank`: RAG 服务设备选择、重排序默认开启与健康检查字段
- `tunnel-access-gate`: 经隧道进入的 AI 计费请求的口令校验、口令生命周期与前端交互
- `admin-credential-hardening`: 管理接口凭据必须显式配置

### Modified Capabilities
<!-- openspec/specs/ 目前为空，无既有 spec 需要 delta -->

## Impact

- 前端：`vite.config.ts`、`pages/ModulesPage.tsx`、`services/api.ts`（新增 `fetchInterpretStream`）、`services/interpretHttp.ts` 或新增 `services/sse.ts`、`tabs/BaziTab.tsx`、`components/QuotaBar.tsx`、`services/deviceHeaders.ts`（口令头与 401 解析）、新增 `components/AccessCodeGate.tsx`、`styles/bazi-visual-demo.css`、`styles/chart-detail.css`
- 后端：`app/api/router.py`（抽取 `_prepare_bazi_interpret` / `_finalize_bazi_interpret_payload`，重写 `/interpret/stream`）、`app/main.py`（注册中间件）、新增 `app/api/access_gate.py`、`app/config.py`（`admin_password: str | None`、`tunnel_access_code_file`）、`app/api/admin_deps.py`、`tests/`（新增 stream 载荷与 gate 测试）
- RAG：`config.py`（`RAG_DEVICE`、telemetry）、`bazi_rag_engine.py`、`build_index.py`、`reranker.py`、`server.py`（`/health` 字段）、`requirements.txt`（去掉 `pywin32`，注明 torch 安装方式）、venv 重装 CUDA torch（约 2.5GB 下载）
- 脚本：`start-rag.sh`、`start-tunnel.sh`、`stop-tunnel.sh`
- 依赖：无新增 npm 包；Python 侧 torch 换 CUDA 构建
- 运行时：前端需重新 `npm run build` 并重启 preview；后端与 RAG 需重启；口令文件路径 `code/backend/data/tunnel_access_code.txt` 需加入 `.gitignore`
