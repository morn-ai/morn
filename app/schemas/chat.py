from typing import List, Optional

from blockcontent import Block
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    """
    Schema for chat requests.
    """
    input: Optional[str] = None
    thread_id: str
    messages: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    """
    Schema for chat responses.
    """
    blocks: list[Block]
