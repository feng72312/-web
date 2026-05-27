from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BAZI_", env_file=".env", extra="ignore")

    app_name: str = "Bazi Fortune API"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Paipan defaults (override via env or future admin UI)
    paipan_sect: int = 2
    early_zishi_mode: str = "midnight"

    # RAG provider: stub | http
    rag_provider: str = "stub"
    rag_http_url: str = ""

    # Cursor SDK (Composer 2.5)
    cursor_api_key: str = ""
    cursor_model: str = "composer-2.5"
    cursor_workspace: str = ""
    # auto=CloudRun/container uses cloud, local dev uses local
    cursor_runtime: str = "auto"


settings = Settings()
