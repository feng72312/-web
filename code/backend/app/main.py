from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.api.router import router
from app.config import settings
from app.core.agent.service import init_agent_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_service = init_agent_service(
        api_key=settings.cursor_api_key,
        model=settings.cursor_model,
        workspace=settings.cursor_workspace,
        runtime=settings.cursor_runtime,
    )
    app.state.agent_service = agent_service
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
