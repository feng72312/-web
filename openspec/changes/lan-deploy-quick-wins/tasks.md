## 1. 样式修复（bazi-report-theming）

- [x] 1.1 `code/frontend/src/styles/bazi-visual-demo.css`：在 `.bazi-report-wuxing-fill` 之后新增 `.bazi-report-wuxing-fill.wx-wood/.wx-fire/.wx-earth/.wx-metal/.wx-water { background: var(--wood|--fire|--earth|--metal|--water) }`
- [x] 1.2 `code/frontend/src/styles/app.css`：在 `:root` 与 `:root[data-theme="dark"]` 各定义 `--detail-head-bg`、`--detail-head-fg`、`--detail-label-bg`、`--detail-alt-bg`（亮色取现值 `#4a4a4a/#fff/#f0ebe3/#f7f3ec`，暗色取 `--wb-section-bg` 系列）
- [x] 1.3 `code/frontend/src/styles/chart-detail.css`：把 `.detail-head th`、`.detail-table .row-label`、`tr.detail-alt td/th.row-label`、`.detail-note-row .note-label` 的硬编码色替换为 1.2 的变量
- [x] 1.4 浏览器验收：八字详盘亮/暗两态截图，五行条有色、暗色下天干/地支/藏干为深底且十神小字可读；抽查紫微、六爻详盘暗色

## 2. 配额条精简（lan-quota-display）

- [x] 2.1 `code/frontend/src/components/QuotaBar.tsx`：删除 `fetchQuotaPersistence`、`storageWarning`、`showRedeem`/`keyInput`/`handleRedeem` 与兑换面板 JSX；只保留 `fetchQuotaStatus` + `quota-refresh` 监听；轮询改 5 分钟；文案改为 "今日 AI 剩余 {freeRemaining} 次"；`status` 为 null 时返回 null
- [x] 2.2 `code/frontend/src/services/deviceHeaders.ts`：402 文案改为 "今日 AI 次数已用完, 明日再试"；401 不再返回 "请先登录"，改为读取 `detail` 或 "请求未授权"（口令分支在 6.x 处理）
- [x] 2.3 全仓搜索 "兑换秘钥" / "人工付款" / "服务端数据尚未持久化" / "请先登录后再使用"，确认前端 `src/` 下无残留（`quotaApi.ts` 中的 `redeemLicenseKey` 保留但不再被引用，若 lint 报 unused export 则加注释说明保留原因）
- [x] 2.4 `npm run lint && npx tsc --noEmit` 通过

## 3. 前端打包优化（frontend-bundle-optimization）

- [x] 3.1 `code/frontend/vite.config.ts`：删除 `modulePreload: false` 与 `minify: false`；新增 `build.rollupOptions.output.manualChunks(id)`：按 `node_modules/` 路径归入 `vendor-react`（react, react-dom, scheduler）、`vendor-antd`（antd, @ant-design, rc-）、`vendor-echarts`（echarts, zrender）、`vendor-motion`（framer-motion, motion）、`vendor-assistant`（@assistant-ui）；其余 node_modules 归 `vendor`
- [x] 3.2 `code/frontend/src/pages/ModulesPage.tsx`：10 个 Tab 改为 `const BaziTab = lazy(() => import("../tabs/BaziTab").then(m => ({ default: m.BaziTab })))` 形式；switch 外层包 `<Suspense fallback={<ModuleSkeleton />}>`；新增 `components/product/ModuleSkeleton.tsx`（复用现有卡片类名，高度 ≥ 480px）
- [x] 3.3 `npm run build`；记录 `du -sh dist/assets` 与 `ls -la dist/assets/*.js | sort -k5 -n | tail -3`；验证每个 js < 1.5MB、总量 < 2.5MB
- [x] 3.4 若 build/运行时因 minify 报错：`build.esbuild = { keepNames: true }` 兜底并记录原因
- [x] 3.5 重启 preview（`code/start-frontend.sh`），浏览器走 首页 → 八字 → 排盘 → 解读 → AI 对话，控制台无报错；网络面板确认首页未加载 `TarotTab`/`ZiweiTab` chunk

## 4. 后端：八字流式解读（bazi-interpret-streaming）

- [x] 4.1 `code/backend/app/api/router.py`：新增 `@dataclass BaziInterpretContext`（chart, sections, excerpts, compressed, judgement_dict, tiered, prompt, interpret_service, knowledge）与 `async def _prepare_bazi_interpret(body, chart, sections, request) -> BaziInterpretContext`，内容为现有 `/interpret` 非融合分支第 636–704 行（判定链、grounded excerpts、legacy rag / knowledge 分支、`build_interpret_prompt`）
- [x] 4.2 `router.py`：新增 `def _finalize_bazi_interpret_payload(ctx, summary, agent_id) -> dict`，内容为现有第 715–758 行（build_response、knowledge、judgement、ruleIdRefs、tieredEvidence*、knowledgeEvidence、confidence*、segments、anchoredRatio 降级）
- [x] 4.3 `router.py`：`/interpret` 非融合分支改为 `ctx = await _prepare_...`；`summary` 计算逻辑（directAnswer 优先、否则 `chat.interpret(ctx.prompt, body.model)` + session bind + 异常回退）保持；末尾 `return {"chart","sections","interpretation": _finalize_...}`
- [x] 4.4 `router.py`：重写 `/interpret/stream`：保留 404/400 前置检查；`event_generator` 依次 `stage("排盘判定")` → `ctx = await _prepare_...` → `stage("检索典籍")`（若 excerpts 非空则带条数）→ `agent_id = await chat.create_session(); chat.set_bootstrap(agent_id, ctx.prompt); chat.bind_chart(chart_key, agent_id); session_store.bind(...)` → `stage("AI 解读")` → `async for chunk, run_id in chat.send_stream(agent_id, ctx.prompt, body.model)` 逐 `delta`；`run_id` 到达时 `done = {"type":"done","chart":ctx.chart,"sections":ctx.sections,"interpretation":_finalize_...(ctx, sanitize_ai_text(full), agent_id)}`；异常 → `error`
- [x] 4.5 确认 `_prepare_bazi_interpret` 中的 `HTTPException(503)`（RAG 不可用）在流式路径里转为 `error` 事件而非 500
- [x] 4.6 `code/backend/tests/test_interpret_stream_parity.py`：用 `TestClient` + monkeypatch 把 `ChatOrchestrator.interpret` 与 `send_stream` 桩为固定文本；同一 `InterpretRequest` 分别打 `/interpret` 与 `/interpret/stream`；解析 SSE，断言事件顺序 `stage+ delta+ done`，断言 `done.interpretation` 的 `judgement`/`tieredEvidence`/`ruleIdRefs`/`knowledgeEvidence`/`segmentStats` 键存在且 `judgement`、`tieredEvidence`、`ruleIdRefs` 与非流式相等；断言 `fusion: true` → 400；断言配额只扣一次（读 `quota_status`）
- [x] 4.7 `pytest tests/test_interpret_stream_parity.py tests/test_quota.py -q` 通过

## 5. 前端：八字流式解读（bazi-interpret-streaming）

- [x] 5.1 新增 `code/frontend/src/services/sse.ts`：`export async function readSseStream<T>(response: Response, onEvent: (payload: T) => void): Promise<void>`（从 `chatApi.ts` 220–254 行提炼：getReader / TextDecoder / `\n\n` 分帧 / `data: ` 解析）
- [x] 5.2 `code/frontend/src/services/chatApi.ts`：`sendChatStream` 改为调用 `readSseStream`，行为不变
- [x] 5.3 `code/frontend/src/services/api.ts`：新增 `export function fetchInterpretStream(body, options, handlers: { onStage, onDelta, onDone(result: InterpretResponse), onError(msg) }): AbortController`；请求头用 `jsonDeviceHeaders(options.model)`；`response.ok` 为假时抛出带 `status` 的错误；`done` 事件组装为 `InterpretResponse` 后 `refreshQuotaBar()` 再 `onDone`
- [x] 5.4 `code/frontend/src/tabs/BaziTab.tsx`：新增 `streamingSummary: string` 与 `interpretStage: string` state；`handleInterpret` 改为：若 `options.fusion` 或流式首个 delta 前失败 → 调 `fetchInterpret`（现有逻辑）；否则 `fetchInterpretStream`，`onStage` 设置阶段文案，`onDelta` 追加 `streamingSummary`，`onDone` 走现有 `setInterpretation` 合并 + timeline + fusionSource + `setChatAgentId`，`onError` 设置错误并保留已显示文本
- [x] 5.5 `BaziTab.tsx` / `components/bazi/BaziReportView.tsx`：解读按钮在 loading 时显示 `interpretStage`；summary 区在 `streamingSummary` 非空且 `interpretation` 尚未更新时渲染 `streamingSummary`（复用现有 summary 样式，末尾加光标类 `.streaming-cursor`）
- [x] 5.6 `npx tsc --noEmit && npm run lint` 通过；浏览器验收：点击解读 3 秒内出现文字；DevTools 把 `/interpret/stream` 改为 404（或临时 `RAG`/`chat` 关闭）验证回退到 `/interpret`

## 6. 隧道口令（tunnel-access-gate）

- [x] 6.1 `code/backend/app/config.py`：新增 `tunnel_access_code_file: str = "data/tunnel_access_code.txt"`（相对 backend 根目录，与现有 quota db 路径解析方式一致）
- [x] 6.2 新增 `code/backend/app/api/access_gate.py`：纯 ASGI 中间件 `AccessGateMiddleware(app, code_file: Path)`；受保护路径正则 `^/api/v1/(?:.+/)?interpret(?:/stream)?$`、`^/api/v1/chat/`、`^/api/v1/rag/search$`；仅当请求含 `cf-connecting-ip` 头且 `read_code()` 非空时校验 `x-access-code`（`secrets.compare_digest`）；失败返回 401 JSON `{"detail":{"code":"access_code_required","message":"请输入访问口令"}}`；`read_code()` 以文件 mtime 为缓存键
- [x] 6.3 `code/backend/app/main.py`：在 CORS 之后 `app.add_middleware(AccessGateMiddleware, code_file=...)`；CORS `allow_headers` 确认包含 `X-Access-Code`（若为 `["*"]` 则无需改）
- [x] 6.4 `code/backend/tests/test_access_gate.py`：使用 `tmp_path` 口令文件 + `TestClient`，覆盖 spec 中六个场景（无头无文件、有头无文件、有头有文件无码、有头有文件对码、有头有文件错码、非保护路径）与"文件删除后立即放行"
- [x] 6.5 `code/start-tunnel.sh`：口令解析顺序 `ZY_TUNNEL_ACCESS_CODE` → `logs/tunnel.code` → `openssl rand -hex 3`；写 `logs/tunnel.code` 与 `backend/data/tunnel_access_code.txt`；成功后输出 `[tunnel] access code: <code>`；`stop-tunnel.sh`：删除 `backend/data/tunnel_access_code.txt`；`start-all.sh`：启动前若口令文件存在且 `logs/tunnel.pid` 进程不在则删除口令文件
- [x] 6.6 `.gitignore` 追加 `code/backend/data/tunnel_access_code.txt` 与 `code/logs/tunnel.code`
- [x] 6.7 `code/frontend/src/services/deviceHeaders.ts`：`jsonPublicHeaders` 追加 `X-Access-Code`（`localStorage.getItem("zy_access_code")` 非空时）；新增 `export class AccessCodeRequiredError extends Error`；`parseApiErrorMessage` 前置检查 `detail.code === "access_code_required"` 并由调用方抛出该错误类型（提供 `throwIfAccessCodeRequired(text, status)` 帮助函数）
- [x] 6.8 新增 `code/frontend/src/components/AccessCodeGate.tsx`：挂载在 `App.tsx` 根部；导出 `promptAccessCode(opts?: { invalid?: boolean }): Promise<string | null>`（模块级 resolver + antd `Modal`，标题 "输入访问口令"，`invalid` 时显示 "口令不正确"）；确认后写 localStorage 并 resolve
- [x] 6.9 新增 `code/frontend/src/services/accessRetry.ts`：`export async function withAccessCodeRetry<T>(run: () => Promise<T>): Promise<T>`：捕获 `AccessCodeRequiredError` → `promptAccessCode({invalid: hadStoredCode})` → 有值重试一次，再失败原样抛出；null 抛 `Error("需要访问口令")`
- [x] 6.10 在 `interpretHttp.postInterpretJson`、`api.ts postJson`、`api.ts fetchInterpretStream`（响应非 ok 分支）、`chatApi.ts` 所有 fetch 入口套 `withAccessCodeRetry`
- [x] 6.11 端到端验收：`start-tunnel.sh` → 手机 4G 打开隧道 URL → 点解读出现口令弹窗 → 输错提示、输对成功；同一时刻局域网电脑无弹窗；`stop-tunnel.sh` 后 `ls code/backend/data/tunnel_access_code.txt` 不存在

## 7. 管理密码（admin-credential-hardening）

- [x] 7.1 `code/backend/app/config.py`：`admin_password: str | None = None`
- [x] 7.2 `code/backend/app/api/admin_deps.py`：`expected_pass` 为空 → `HTTPException(403, "admin disabled: set ADMIN_PASSWORD")`；比对改 `secrets.compare_digest`
- [x] 7.3 `code/backend/tests/test_admin.py`：fixture 通过 `monkeypatch.setattr(settings, "admin_password", "test-admin")` 注入；新增未配置 → 403 用例
- [x] 7.4 `code/backend/.env`：追加 `ADMIN_PASSWORD=<openssl rand -base64 18 生成>`，在任务进度中记录已设置（不写入任务文件明文）
- [x] 7.5 `pytest tests/test_admin.py -q` 通过

## 8. RAG GPU 与重排序（rag-gpu-rerank）

- [x] 8.1 临时 venv 验证：`uv venv /tmp/rag-cuda --python 3.11 && uv pip install --python /tmp/rag-cuda torch --index-url https://download.pytorch.org/whl/cu124 && uv pip install --python /tmp/rag-cuda sentence-transformers==2.7.0 transformers==4.40.2`；`python -c "import torch;print(torch.cuda.is_available())"` 为 True 且 `CrossEncoder("BAAI/bge-reranker-base", device="cuda")` 可加载
- [x] 8.2 正式 venv：`uv pip install --python code/rag/.venv torch --index-url https://download.pytorch.org/whl/cu124`（覆盖 cpu 版）；再次验证 `torch.cuda.is_available()`
- [x] 8.3 `code/rag/requirements.txt`：删除 `pywin32>=306`；顶部注释 `# torch: install separately -> uv pip install torch --index-url https://download.pytorch.org/whl/cu124 (or /cpu)`
- [x] 8.4 `code/rag/config.py`：新增 `RAG_DEVICE = os.environ.get("RAG_DEVICE", "auto")` 与 `def resolve_device() -> str`（auto → torch.cuda.is_available()）；新增 `CHROMA_SETTINGS = chromadb.config.Settings(anonymized_telemetry=False)`
- [x] 8.5 `code/rag/bazi_rag_engine.py` 与 `code/rag/build_index.py`：`SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL, device=resolve_device())`；`chromadb.PersistentClient(path=..., settings=CHROMA_SETTINGS)`
- [x] 8.6 `code/rag/reranker.py`：`CrossEncoder(rerank_model_name(), device=resolve_device())`
- [x] 8.7 `code/rag/server.py`：`/health` 返回新增 `chunks`（引擎已加载 → `collection.count()`；否则读 `data/index_report.json` 的 `chunks_total`）、`device`、`rerank`、`embedModel`、`rerankModel`
- [x] 8.8 `code/start-rag.sh`：`export RAG_RERANK="${RAG_RERANK:-1}"`、`export RAG_DEVICE="${RAG_DEVICE:-auto}"`
- [x] 8.9 重启 RAG；`curl 127.0.0.1:8100/health` 显示 `device: cuda, rerank: true, chunks: 67269`；`nvidia-smi` 出现 rag venv 进程；连续 10 次 `/search` 中位数 < 500ms；`rag.log` 无 telemetry 报错
- [x] 8.10 后端 `curl 127.0.0.1:8002/api/v1/rag/status`（或前端八字页）显示索引条数非 0 且来自 `/health`

## 9. 集成验收与收尾

- [x] 9.1 重启后端（`start-backend.sh`），`pytest -q` 全量通过
- [x] 9.2 重新 `npm run build` + 重启 preview；局域网浏览器完整走一遍：首页 → 八字排盘 → 流式解读 → 深色主题详盘 → AI 对话 → 塔罗（非流式仍正常）
- [x] 9.3 记录前后对比数据到任务进度：主包大小、首屏 JS 总量、解读首字时间、RAG `/search` 延迟
- [x] 9.4 `git add` 本 change 涉及文件（排除 `.tasks/`、口令文件、`.env`），提交信息概述七项能力
