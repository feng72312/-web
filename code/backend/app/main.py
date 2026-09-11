from contextlib import asynccontextmanager

import logging
import os



from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import PlainTextResponse



from app.api.liuyao_router import router as liuyao_router
from app.api.meihua_router import router as meihua_router
from app.api.liuren_router import router as liuren_router
from app.api.hepan_router import router as hepan_router
from app.api.utils_router import router as utils_router
from app.api.ziwei_router import router as ziwei_router
from app.api.xingming_router import router as xingming_router
from app.api.tianxiang_router import router as tianxiang_router
from app.api.qimen_router import router as qimen_router
from app.api.fengshui_router import router as fengshui_router
from app.api.router import router
from app.api.admin_router import router as admin_router
from app.api.auth_router import router as auth_router
from app.api.quota_router import router as quota_router
from app.api.stats import router as stats_router
from app.api.tarot_router import router as tarot_router
from app.api.platform_router import router as platform_router
from app.api.access_gate import AccessGateMiddleware

from app.config import settings

from app.core.agent.chat_orchestrator import init_chat_orchestrator

from app.core.agent.deepseek import init_deepseek_client
from app.core.agent.service import init_agent_service

from app.core.agent.session_store import AgentSessionStore
from app.core.knowledge.factory import init_knowledge_service
from app.core.admin.session import AdminSessionStore
from app.core.concurrency.cpu_pool import init_cpu_pool, shutdown_cpu_pool
from app.core.concurrency.interpret_limit import InterpretConcurrencyLimiter
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaStore, resolve_quota_db_path
from app.core.stats.store import UsageStatsStore, resolve_stats_db_path



logger = logging.getLogger(__name__)

_session_store = AgentSessionStore()





@asynccontextmanager

async def lifespan(app: FastAPI):

    deepseek_client = init_deepseek_client(

        api_key=settings.deepseek_api_key,

        base_url=settings.deepseek_base_url,

    )

    cursor_service = None
    start_cursor = bool((settings.cursor_api_key or "").strip()) and not os.environ.get(
        "PYTEST_CURRENT_TEST"
    )
    if start_cursor:
        cursor_service = init_agent_service(
            api_key=settings.cursor_api_key,
            model=settings.cursor_model,
            workspace=settings.cursor_workspace,
            runtime="local",
        )
        try:
            await cursor_service.startup()
        except Exception:
            logger.exception("cursor agent bridge failed to start; continuing without Composer")
            cursor_service = None

    orchestrator = init_chat_orchestrator(

        cursor=cursor_service if cursor_service and cursor_service.enabled else None,

        deepseek=deepseek_client if deepseek_client.enabled else None,

        sessions=_session_store,

    )

    app.state.agent_service = cursor_service if cursor_service and cursor_service.enabled else None

    app.state.deepseek_client = deepseek_client

    app.state.chat_orchestrator = orchestrator

    app.state.session_store = _session_store
    app.state.stats_store = UsageStatsStore(resolve_stats_db_path())
    quota_path = resolve_quota_db_path()
    app.state.quota_service = QuotaService(QuotaStore(quota_path))
    from app.core.quota.persistence import inspect_sqlite_path

    quota_info = inspect_sqlite_path(quota_path)
    if not quota_info["likelyPersistent"]:
        logger.warning(
            "quota storage may not persist across redeploy: path=%s cos_mount=%s "
            "(enable COS mount on bazi-api, see docs/cloud-persistent-storage-mount.md)",
            quota_info["dbPath"],
            quota_info["cosMountDetected"],
        )
    app.state.admin_session_store = AdminSessionStore(
        ttl_seconds=settings.admin_session_ttl_hours * 3600
    )
    knowledge_service = init_knowledge_service()
    app.state.knowledge_service = knowledge_service
    init_cpu_pool(settings.cpu_pool_max_workers)
    app.state.interpret_limiter = InterpretConcurrencyLimiter(
        settings.interpret_max_concurrent,
        settings.interpret_queue_wait_seconds,
        settings.interpret_max_waiting,
    )
    logger.info(
        "interpret concurrency max=%s max_waiting=%s queue_wait_s=%s cpu_pool_workers=%s",
        settings.interpret_max_concurrent,
        settings.interpret_max_waiting,
        settings.interpret_queue_wait_seconds,
        settings.cpu_pool_max_workers,
    )
    logger.info(
        "knowledge config enabled=%s nodes=%s dir=%s",
        knowledge_service.enabled,
        knowledge_service.store.stats().get("nodeCount"),
        knowledge_service.store.data_dir,
    )
    logger.info(
        "rag config provider=%s url=%s category=%s",
        settings.rag_provider,
        settings.rag_http_url or "(empty)",
        settings.rag_default_category,
    )

    yield

    if cursor_service is not None:
        await cursor_service.shutdown()
    shutdown_cpu_pool()





app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)





@app.get("/health", response_class=PlainTextResponse)

async def health() -> str:

    return "ok"



def _tunnel_code_file():
    from pathlib import Path

    raw = (settings.tunnel_access_code_file or "").strip() or "data/tunnel_access_code.txt"
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    return path


app.add_middleware(AccessGateMiddleware, code_file=_tunnel_code_file())
app.add_middleware(

    CORSMiddleware,

    allow_origins=settings.cors_origins,

    allow_origin_regex=r"https://.*\.tcloudbaseapp\.com",

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)



app.include_router(router)
app.include_router(liuyao_router)
app.include_router(meihua_router)
app.include_router(qimen_router)
app.include_router(fengshui_router)
app.include_router(liuren_router)
app.include_router(ziwei_router)
app.include_router(xingming_router)
app.include_router(tianxiang_router)
app.include_router(hepan_router)
app.include_router(utils_router)
app.include_router(quota_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(tarot_router)
app.include_router(stats_router)
app.include_router(platform_router)
