from pydantic import BaseModel


class QuotaPersistenceResponse(BaseModel):
    quotaDbPath: str
    statsDbPath: str
    quota: dict[str, object]
    stats: dict[str, object]
    likelyPersistent: bool
    warning: str | None = None
