from pydantic import BaseModel


class RagStatusResponse(BaseModel):
    provider: str
    httpUrl: str
    serviceOk: bool
    serviceMessage: str
    chunks: int = 0
    filesTotal: int = 0
    chunksTotal: int = 0
    builtAt: str | None = None
