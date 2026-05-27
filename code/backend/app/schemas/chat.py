from typing import Any, Dict, List, Optional



from pydantic import BaseModel, Field





class ChatInitRequest(BaseModel):

    chart: Dict[str, Any]

    sections: List[dict] = Field(default_factory=list)





class ChatInitResponse(BaseModel):

    agentId: str





class RagSearchResponse(BaseModel):

    query: str

    excerpts: List[dict]





class ChatHistoryMessage(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    agentId: str
    messages: List[ChatHistoryMessage]


class ChatSendRequest(BaseModel):

    agentId: str = Field(min_length=1)

    message: str = Field(min_length=1, max_length=4000)

    model: Optional[str] = None





class ChatSendResponse(BaseModel):

    agentId: str

    runId: str

    text: str





class ChatModelInfo(BaseModel):

    id: str

    label: str

    tag: str

    provider: str





class ChatStatusResponse(BaseModel):

    enabled: bool

    model: str

    runtime: str = ""

    models: List[ChatModelInfo] = Field(default_factory=list)

    cursorEnabled: bool = False

    deepseekEnabled: bool = False

