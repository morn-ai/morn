import json
import logging
from typing import Annotated, AsyncGenerator

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette import EventSourceResponse

from app.config.agent_config import AgentConfig
from app.schemas.chat import ChatCompletionRequest
from app.schemas.auth import TokenData
from app.api.auth import require_auth

router = APIRouter()
config = AgentConfig()

@router.post("/api/v1/chat/completions")
async def chat_completion(
    request: ChatCompletionRequest,
    current_user: Annotated[TokenData, Depends(require_auth)]
):
    logging.info(f"receive chat request: {request}")

    if request.stream:
        return EventSourceResponse(stream_response(request))
    else:
        return await non_stream_response(request)


async def non_stream_response(request: ChatCompletionRequest) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{config.openai_api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.openai_model,
                    "messages": [msg.model_dump() for msg in request.messages],
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"OpenAI API error: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


async def stream_response(request: ChatCompletionRequest) -> AsyncGenerator[dict, None]:
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "POST",
                f"{config.openai_api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.openai_model,
                    "messages": [msg.model_dump() for msg in request.messages],
                    "stream": True
                },
                timeout=30.0
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            yield {
                                "event": "message",
                                "data": "[DONE]"
                            }
                            break
                        try:
                            json_data = json.loads(data)
                            yield {
                                "event": "message",
                                "data": json.dumps(json_data)
                            }
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            logging.error(f"OpenAI API error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": "Internal server error"})
            }
