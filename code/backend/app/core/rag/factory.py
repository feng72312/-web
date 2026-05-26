from __future__ import annotations

from app.config import settings
from app.core.rag.base import RagProvider
from app.core.rag.http import HttpRagProvider
from app.core.rag.stub import StubRagProvider


def build_rag_provider() -> RagProvider:
    if settings.rag_provider == "http" and settings.rag_http_url:
        return HttpRagProvider(settings.rag_http_url)
    return StubRagProvider()
