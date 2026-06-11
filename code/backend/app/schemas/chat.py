from typing import Any, Dict, List, Optional



from pydantic import BaseModel, Field





class ChatInitRequest(BaseModel):

    chart: Dict[str, Any]

    sections: List[dict] = Field(default_factory=list)





class ChatInitResponse(BaseModel):

    agentId: str


class ChatGeneralInitRequest(BaseModel):
    scenario: str = "general"
    title: Optional[str] = None
    initialPrompt: Optional[str] = None


class ChatGeneralInitResponse(BaseModel):
    agentId: str
    title: str
    scenario: str


class ChatFusionSource(BaseModel):
    moduleId: str = Field(min_length=1, max_length=32)
    moduleLabel: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=120)
    question: Optional[str] = Field(default=None, max_length=500)
    chartSnapshot: Dict[str, Any] = Field(default_factory=dict)
    summaryPlain: Optional[str] = Field(default=None, max_length=8000)
    summaryProfessional: Optional[str] = Field(default=None, max_length=8000)
    createdAt: Optional[str] = Field(default=None, max_length=40)


class ChatFusionInitRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=160)
    sources: List[ChatFusionSource] = Field(min_length=2, max_length=6)


class ChatFusionInitResponse(BaseModel):
    agentId: str
    title: str
    scenario: str
    sourceCount: int





class RagSearchResponse(BaseModel):

    query: str

    excerpts: List[dict]





class ChatHistoryMessage(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    agentId: str
    messages: List[ChatHistoryMessage]


class ChatSeedInterpretRequest(BaseModel):
    agentId: str = Field(min_length=1)
    summaryPlain: Optional[str] = None
    summaryProfessional: Optional[str] = None
    model: Optional[str] = None


class ChatSeedInterpretResponse(BaseModel):
    agentId: str
    added: int


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

    tier: str = "大师"

    tierRank: int = 2





class ChatStatusResponse(BaseModel):

    enabled: bool

    model: str

    runtime: str = ""

    models: List[ChatModelInfo] = Field(default_factory=list)

    cursorEnabled: bool = False

    deepseekEnabled: bool = False

