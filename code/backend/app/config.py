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
    rag_default_category: str = "01八字命理"
    liuyao_rag_category: str = "02六爻卜筮"
    meihua_rag_category: str = "03梅花易学"
    qimen_rag_category: str = "04奇门遁甲"
    liuren_rag_category: str = "05大六壬"

    # Cursor SDK (Composer 2.5)
    cursor_api_key: str = ""
    cursor_model: str = "composer-2.5"
    cursor_workspace: str = ""
    # auto=CloudRun/container uses cloud, local dev uses local
    cursor_runtime: str = "auto"

    # DeepSeek OpenAI-compatible API
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # Structured knowledge graph (compressed nodes)
    knowledge_enabled: bool = True
    knowledge_data_dir: str = ""
    knowledge_direct_answer_enabled: bool = True
    knowledge_rag_fallback: bool = True
    knowledge_use_legacy_rag_first: bool = False

    # Usage stats SQLite (set on cloud to COS mount path, e.g. /mnt/data/usage_stats.db)
    stats_db_path: str = ""

    # AI quota / license keys SQLite
    quota_db_path: str = ""

    # Admin console (override via env in production)
    admin_username: str = "fengge"
    admin_password: str = "1234567890.0aa"
    admin_session_ttl_hours: int = 24

    # Bazi + Liuyao dual-channel fusion (method B)
    fusion_enabled: bool = True
    fusion_default_scope: str = "life_outline"


settings = Settings()
