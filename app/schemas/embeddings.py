from typing import List, Optional, Union
from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    model: str = "BAAI/bge-large-zh-v1.5"
    input: Union[str, List[str]]


class EmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int


class EmbeddingUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class EmbeddingResponse(BaseModel):
    model: str
    data: List[EmbeddingData]
    usage: EmbeddingUsage 
