## Context

ZY 当前在单台 Ubuntu 24.04 服务器（RTX 4090、125GB 内存）上以三进程方式运行：Vite preview 托管前端并把 `/api` 反代到 FastAPI 后端（127.0.0.1:8002），后端再调用 RAG 服务（127.0.0.1:8100，Chroma + bge-small-zh 嵌入）和 DeepSeek 云 API。CloudBase 登录已停用，配额上限为 9999，局域网用户无需登录。外网通过 `start-tunnel.sh` 起 cloudflared quick tunnel 临时暴露 5173。

实测现状：

- `vite.config.ts` 在 CloudBase 登录提交（e538d7c）中写死了 `minify: false` / `modulePreload: false`，无注释说明原因；主 chunk 5.0MB（gzip ≈ 1MB），10 个模块 Tab 在 `ModulesPage.tsx` 静态导入。
- `/interpret`（八字，非流式）会跑 `BaziJudgementChain`、分级证据、段落锚点、置信度并组装完整载荷；`/interpret/stream` 是早期精简版，只有 RAG 检索 + LLM 流式，缺判定链等字段，前端因此从未使用它。其余模块各有独立 `/xxx/interpret`，均非流式。
- `chat_orchestrator.send_stream` 已支持 DeepSeek 流式并在结束时产出 `run_id`；`chatApi.ts` 已有一套 SSE 读取循环（`data: ` 前缀 + `\n\n` 分帧）。
- `.bazi-report-wuxing-fill` 只定义高度/圆角，无任何 `.wx-*` 背景规则；`chart-detail.css:46` 的 `.detail-table tr.detail-alt td { background: #f7f3ec }` 硬编码浅色，覆盖了 `bazi-visual-demo.css` 里用 rgba 写的暗色友好规则（同特异性，后加载者胜）。
- `QuotaBar` 每 60 秒轮询 `/quota/status` 与 `/quota/persistence`，后者返回非持久化即显示"请联系运营配置云存储挂载"。
- RAG：`SentenceTransformerEmbeddingFunction(model_name)` 在 chromadb 0.5.23 中 `device` 默认 `"cpu"`；`CrossEncoder(name)` 默认自动选 cuda。venv 里 torch 为 `2.13.0+cpu`，`RAG_RERANK` 未在 Linux 脚本中设置。`/health` 不返回 chunk 数，后端只能回退读 `index_report.json`。
- 后端日志显示 400+ 次公网 IP 请求（隧道链接已外泄或被扫描）。cloudflared 对每个经隧道的请求注入 `CF-Connecting-IP` 头，Vite 反代会原样透传；局域网直连请求没有这个头。
- `settings.admin_password` 默认值为明文 `"1234567890.0aa"`，`admin_deps.py` 直接比对。

## Goals / Non-Goals

**Goals:**

- 生产包体减半以上，模块代码按需加载，隧道场景首屏明显变快
- 八字解读从"转圈 60 秒"变为"1–2 秒内开始逐字出现"，且最终载荷与非流式完全一致（判定链、证据、置信度不丢）
- 修掉两个肉眼可见的主题/样式 bug
- 去掉 CloudBase 遗留提示与兑换入口，不动后端配额模型
- RAG 利用 4090：嵌入与重排序跑 GPU，重排序默认开启，健康检查能反映真实状态
- 隧道开启期间，外部访客必须持口令才能触发 AI 计费请求；局域网用户零感知
- 管理接口没有默认密码

**Non-Goals:**

- 不做路由/URL 深链改造、不做 PWA、不做导出分享（后续 change）
- 不把塔罗/六爻/紫微等其他模块改为流式（本次只沉淀可复用的前后端流式模式）
- 不引入 Nginx、HTTPS、systemd 自启（部署层改造另开 change）
- 不重做"炫酷"视觉（氛围背景、字体、图表化命盘）——这是独立的设计工作
- 不恢复登录/账号体系

## Decisions

### D1. 打包：开 esbuild minify + 手动 vendor 分包 + Tab 级 `React.lazy`

- 选择：`build.minify` 恢复默认（esbuild），删除 `modulePreload: false`，`rollupOptions.output.manualChunks` 按包名归入 `vendor-react`（react/react-dom/scheduler）、`vendor-antd`（antd/@ant-design/rc-*）、`vendor-echarts`、`vendor-motion`（framer-motion）、`vendor-assistant`（@assistant-ui）；`ModulesPage.tsx` 的 10 个 Tab 改为 `lazy(() => import(...))` 并用一个 `<Suspense fallback={<ModuleSkeleton/>}>` 包裹 switch。
- 备选：只开 minify 不分包（收益约 60%，但 antd/echarts 仍首屏全下载）；用 `vite-plugin-chunk-split` 等插件（多一个依赖，收益相同）。
- 理由：零新依赖；minify 关闭找不到保留理由，若构建后出现运行时报错（最可能是某库依赖函数名），可在 `esbuild.keepNames: true` 下兜底。

### D2. 八字流式：把非流式路径拆成"准备 → 生成 → 收尾"三段，流式端点复用前后两段

- 选择：在 `router.py` 抽出
  - `_prepare_bazi_interpret(body, chart, request) -> BaziInterpretContext`：跑判定链、解析 tiered evidence、决定 excerpts / compressed、构造 prompt（即现有 `/interpret` 第 636–704 行逻辑）
  - `_finalize_bazi_interpret_payload(ctx, summary, agent_id) -> dict`：现有第 715–758 行逻辑（knowledge、judgement、ruleIdRefs、segments、confidenceBand 等）
  - `/interpret` 非融合分支改为调用这两段 + `chat.interpret`
  - `/interpret/stream` 改为：`stage("排盘判定")` → prepare → `stage("检索典籍")` → `stage("AI 解读")` → `chat.send_stream` 逐 `delta` → 收到 `run_id` 后 `_finalize_bazi_interpret_payload(ctx, full_text, agent_id)` 作为 `done.interpretation`，并附 `chart` 与 `sections`。
  - 会话语义与非流式对齐：流式路径每次 `create_session` + `set_bootstrap(prompt)`，不复用旧 `agent_id`（非流式 `chat.interpret` 就是这么做的），避免"上次问事的上下文污染这次解读"。
- SSE 事件协议（`text/event-stream`，每帧 `data: <json>\n\n`）：
  - `{"type":"stage","text":string}`
  - `{"type":"delta","text":string}`
  - `{"type":"done","chart":..., "sections":..., "interpretation":...}`（结构与非流式响应完全一致）
  - `{"type":"error","message":string}`
- 前端：`services/sse.ts` 抽出通用 `readSseStream(response, onEvent)`（从 `chatApi.ts` 的读取循环提炼，chatApi 改为调用它）；`api.ts` 新增 `fetchInterpretStream(body, options, handlers): AbortController`；`BaziTab.handleInterpret` 改为：先清空 `streamingText`，`onStage` 更新按钮文案，`onDelta` 累加到 `streamingText` 并在 summary 区实时渲染，`onDone` 走现有 `setInterpretation` 合并逻辑。
- 回退：若 `fetch` 在拿到首个 `delta` 之前失败（网络错、404 chat 未配置、400 fusion）、或 `options.fusion === true`，则调用现有 `fetchInterpret` 非流式。首个 delta 之后出错则显示错误，不重试（避免双倍计费）。
- 配额：`/interpret/stream` 已 `Depends(consume_interpret_quota)`，与非流式一致，不变。
- 备选：让非流式接口先返回骨架、前端再轮询——改动更大，体验不如 SSE；WebSocket——反代与隧道配置更麻烦。

### D3. 样式修复：补规则 + 用变量替换硬编码色

- `bazi-visual-demo.css` 在 `.bazi-report-wuxing-fill` 之后新增 `.bazi-report-wuxing-fill.wx-wood/fire/earth/metal/water { background: var(--wood|--fire|...) }`（与 683–687 行 `.mystic-wuxing-fill` 的写法一致）。
- `chart-detail.css` 的 `.detail-table .row-label`、`tr.detail-alt td/th` 背景改为主题变量（复用 `--wb-section-bg` 或新增 `--detail-alt-bg`，在 `:root` 与 `:root[data-theme="dark"]` 各定义一份）；`.detail-head th` 与 `.detail-note-row .note-label` 的 `#4a4a4a` 同步处理。
- 备选：在 `bazi-visual-demo.css` 里提高特异性覆盖——治标，其他使用 `.detail-table` 的模块（紫微、六爻详盘）暗色下仍白底。

### D4. 配额条：删除持久化探测与兑换面板，保留"次数"只读展示

- `QuotaBar` 移除 `fetchQuotaPersistence` 调用、`storageWarning`、`showRedeem` 面板与"兑换秘钥"按钮；保留 `fetchQuotaStatus` 与 `quota-refresh` 事件监听，展示"今日 AI 剩余 N 次"。轮询间隔从 60s 放宽到 5 分钟（有事件驱动刷新）。
- `deviceHeaders.parseApiErrorMessage` 的 402 文案改为"今日 AI 次数已用完, 明日再试"；401 文案不再提"登录"，改由 D6 的口令逻辑处理。
- 后端 `/quota/persistence`、`/quota/redeem`、license 表全部保留不动，将来恢复付费只需还原前端。
- 备选：整块删掉 `QuotaBar`——但"剩余次数"对排查限流仍有用，且组件已挂在多处布局中。

### D5. RAG GPU：设备由环境变量决定，脚本默认开重排序

- `config.py` 新增 `RAG_DEVICE = os.environ.get("RAG_DEVICE", "auto")`，`resolve_device()`：`auto` 时 `torch.cuda.is_available()` 则 `cuda` 否则 `cpu`；`ANONYMIZED_TELEMETRY` 通过 `chromadb.config.Settings(anonymized_telemetry=False)` 关闭。
- `bazi_rag_engine.py` / `build_index.py` 的 `SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL, device=resolve_device())`；`reranker.py` 的 `CrossEncoder(name, device=resolve_device())`。
- `server.py /health` 增加 `chunks`（从已加载 collection `count()`，未加载时读 `index_report.json`）、`device`、`rerank: bool`、`embedModel`、`rerankModel`。后端 `status.py` 已能消费 `chunks` 字段。
- `start-rag.sh` 默认 `export RAG_RERANK="${RAG_RERANK:-1}"`、`RAG_DEVICE="${RAG_DEVICE:-auto}"`。
- venv：`uv pip install --python rag/.venv torch --index-url https://download.pytorch.org/whl/cu124`（约 2.5GB；4090 驱动支持 CUDA 12.x）。`requirements.txt` 移除 `pywin32`（Linux 装不上），顶部注释说明 torch 单独安装。
- 备选：保留 CPU、只开重排序——bge-reranker-base 在 CPU 上对 topK=20 重排约 1–2 秒，可接受但浪费 GPU；用 GPU 但不改 `/health`——后端仍靠回退读文件，状态不真实。
- 显存预算：bge-small-zh + bge-reranker-base 合计 < 1.5GB，与 Wan2GP（当前占 1.3GB，生成时可能到 20GB+）共存无压力；若 Wan2GP 满载，`RAG_DEVICE=cpu` 可随时回退。

### D6. 隧道口令：后端中间件按 `CF-Connecting-IP` 判定来源，口令走文件共享

- 后端新增 `app/api/access_gate.py`（Starlette `BaseHTTPMiddleware` 或纯 ASGI 中间件）：
  - 受保护路径正则：`/api/v1/(.*/)?interpret(/stream)?$`、`/api/v1/chat/`、`/api/v1/rag/search`
  - 触发条件：请求含 `CF-Connecting-IP` 头 **且** `settings.tunnel_access_code_file` 存在且非空
  - 校验：`X-Access-Code` 头与文件内容（strip）常量时间比较；失败返回 `401 {"detail":{"code":"access_code_required","message":"请输入访问口令"}}`
  - 文件内容按 mtime 缓存，避免每次读盘
- `start-tunnel.sh`：口令来源优先 `ZY_TUNNEL_ACCESS_CODE` 环境变量，否则读 `logs/tunnel.code`（上次用的），都没有则 `openssl rand -hex 3` 生成 6 位；写入 `backend/data/tunnel_access_code.txt` 并在输出里同时打印 URL 和口令。`stop-tunnel.sh` 删除 `tunnel_access_code.txt`（`logs/tunnel.code` 保留以便下次复用同一口令）。
- 前端：`deviceHeaders.jsonPublicHeaders` 追加 `X-Access-Code`（来自 `localStorage.zy_access_code`，无则不带）；`parseApiErrorMessage` 识别 `detail.code === "access_code_required"` 抛出 `AccessCodeRequiredError`；新增 `components/AccessCodeGate.tsx`（antd `Modal` + 单输入框），通过 `promptAccessCode(): Promise<string|null>` 供服务层调用；`interpretHttp.postInterpretJson`、`api.ts` 的 `postJson`、`chatApi` 流式与非流式入口在捕获该错误时 `await promptAccessCode()`，用户提交后重试一次，取消则把错误抛给调用方。
- 为什么不用 Cloudflare Access：quick tunnel（无账号、随机域名）不支持 Access 策略；改为 named tunnel 需要 Cloudflare 账号与域名，超出"临时开关"需求。
- 为什么不在 Vite 层拦：preview server 没有中间件能力，且真正要保护的是后端计费接口而非静态资源。
- 为什么用文件而不是环境变量：后端常驻运行，环境变量要重启才能生效；文件让"开隧道 → 立即生效 / 关隧道 → 立即失效"不重启。
- 局限：`CF-Connecting-IP` 可被局域网用户伪造来"触发"校验（只会让自己多输一次口令，无害）；反过来外部请求无法去掉这个头（由 cloudflared 边缘注入）。

### D7. 管理密码：无默认值，缺省即关闭管理接口

- `config.py`：`admin_password: str | None = None`（pydantic-settings 从 `.env` 的 `ADMIN_PASSWORD` 读取）。
- `admin_deps.py`：`expected_pass` 为空时直接 `403 {"detail":"admin disabled: set ADMIN_PASSWORD"}`；非空时保持现有比对但改用 `secrets.compare_digest`。
- `tests/test_admin.py` 通过 `monkeypatch.setattr(settings, "admin_password", "...")` 注入。
- 服务器 `.env` 需补 `ADMIN_PASSWORD=<新值>`（执行时由用户提供或生成随机值写入并告知）。

## Risks / Trade-offs

- [minify 后某第三方库依赖 `Function.name` 报错] → 构建后跑 `npm run build && npm run preview` 并用浏览器走通首页 / 八字排盘 / 解读 / AI 对话；若出错，`build.esbuild = { keepNames: true }`。
- [Tab 懒加载导致切换模块时闪一下空白] → `Suspense fallback` 用与现有卡片同高的骨架；Vite 会为每个 Tab 生成独立 chunk，局域网内加载 < 50ms。
- [流式路径与非流式路径行为漂移] → 两者共用 `_prepare` / `_finalize`；新增测试用同一份输入分别调用两条路径，断言 `done.interpretation` 除 `summary`/`agentId` 外与非流式响应逐键相等。
- [流式中途断线导致配额已扣但没结果] → 与聊天流式现状一致；`error` 事件文案提示"本次不重复计费, 可直接重试"（配额 9999 下实际无感）。
- [Vite 反代对 SSE 缓冲] → `/chat/stream` 已在同一反代下正常逐字输出，说明 http-proxy 未缓冲；`/interpret/stream` 沿用同配置。
- [CUDA torch 下载 2.5GB 失败或与 sentence-transformers 2.7.0 不兼容] → 先在临时 venv 验证 `import torch; torch.cuda.is_available()` 与 `CrossEncoder` 能加载，再替换正式 venv；失败时 `RAG_DEVICE=cpu` 保持现状。
- [重排序开启后检索延迟上升] → GPU 上 bge-reranker-base 重排 20 条 < 100ms；`/health` 暴露 `rerank` 便于确认；实测 `/search` 延迟写入任务验收。
- [口令文件被误留、局域网用户被要求输口令] → 局域网请求无 `CF-Connecting-IP`，中间件不介入；`stop-tunnel.sh` 删文件；`start-all.sh` 启动时若发现口令文件但隧道 PID 不存在则清理。
- [删除 `admin_password` 默认值导致现有管理脚本 403] → 属预期 BREAKING；`.env` 补值即可，在任务中显式列出。
- [`.detail-table` 变量化影响其他模块详盘] → 这是有意的（统一暗色修复），验收时抽查紫微/六爻详盘亮暗两态。

## Migration Plan

1. 后端、RAG 代码改动合入后：`uv pip install` CUDA torch → 重启 RAG（`start-rag.sh`）→ `curl /health` 确认 `device: cuda, rerank: true, chunks: 67269`。
2. 重启后端，`curl` 验证：局域网直连 `/interpret` 200；带 `CF-Connecting-IP` 且无口令文件 200；有口令文件无头 401；有头 200。
3. 前端 `npm run build`，比较 `dist/assets` 总大小与最大 chunk；重启 preview；浏览器验收流式解读、暗色主题、配额条。
4. `start-tunnel.sh` 起隧道，用手机 4G 走隧道验证口令弹窗与通过后可解读；`stop-tunnel.sh` 后口令文件消失。
5. 回滚：所有改动在一个 git 提交范围内，`git revert` 即可；RAG venv 的 torch 回滚为 `uv pip install torch --index-url https://download.pytorch.org/whl/cpu`。

## Open Questions

- `ADMIN_PASSWORD` 的新值由用户提供还是执行时随机生成写入 `.env` 并回报？（默认：随机生成并回报）
- 隧道口令是否每次开启都换新（更安全）还是复用上次（分享链接的人不用重发口令）？（默认：复用 `logs/tunnel.code`，可用 `ZY_TUNNEL_ACCESS_CODE` 覆盖）
