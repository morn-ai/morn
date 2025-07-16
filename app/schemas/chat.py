from typing import List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    stream: Optional[bool] = False


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: Optional[dict] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[dict]


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
