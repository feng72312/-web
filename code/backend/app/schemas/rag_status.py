from pydantic import BaseModel


class RagStatusResponse(BaseModel):
    provider: str
    httpUrl: str
    serviceOk: bool
    serviceMessage: str
    chunks: int = 0
