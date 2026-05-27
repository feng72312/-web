from contextlib import asynccontextmanager

import logging



from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import PlainTextResponse



from app.api.liuyao_router import router as liuyao_router
from app.api.router import router
from app.api.stats import router as stats_router

from app.config import settings

from app.core.agent.chat_orchestrator import init_chat_orchestrator

from app.core.agent.deepseek import init_deepseek_client

from app.core.agent.service import init_agent_service

from app.core.agent.session_store import AgentSessionStore
from app.core.stats.store import UsageStatsStore, default_stats_db_path



logger = logging.getLogger(__name__)

_session_store = AgentSessionStore()





@asynccontextmanager

async def lifespan(app: FastAPI):

    agent_service = init_agent_service(

        api_key=settings.cursor_api_key,

        model=settings.cursor_model,

        workspace=settings.cursor_workspace,

        runtime=settings.cursor_runtime,

    )

    deepseek_client = init_deepseek_client(

        api_key=settings.deepseek_api_key,

        base_url=settings.deepseek_base_url,

    )

    orchestrator = init_chat_orchestrator(

        cursor=agent_service if agent_service.enabled else None,

        deepseek=deepseek_client if deepseek_client.enabled else None,

        sessions=_session_store,

    )

    app.state.agent_service = agent_service

    app.state.deepseek_client = deepseek_client

    app.state.chat_orchestrator = orchestrator

    app.state.session_store = _session_store
    app.state.stats_store = UsageStatsStore(default_stats_db_path())
    logger.info(
        "rag config provider=%s url=%s category=%s",
        settings.rag_provider,
        settings.rag_http_url or "(empty)",
        settings.rag_default_category,
    )

    try:

        await agent_service.startup()

    except Exception:

        logger.exception("cursor agent startup failed; api stays up without bridge")

    yield

    try:

        await agent_service.shutdown()

    except Exception:

        logger.exception("cursor agent shutdown failed")





app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)





@app.get("/health", response_class=PlainTextResponse)

async def health() -> str:

    return "ok"



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
app.include_router(stats_router)

