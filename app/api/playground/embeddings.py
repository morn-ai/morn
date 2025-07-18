import logging
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import require_auth
from app.config.agent_config import config
from app.schemas.auth import TokenData
from app.schemas.embeddings import EmbeddingRequest, EmbeddingResponse

router = APIRouter()


@router.post("/api/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    current_user: Annotated[TokenData, Depends(require_auth)]
):
    """
    Create embeddings using SiliconFlow API
    """
    logging.info(f"receive embedding request: {request}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{config.openai_api_base}/embeddings",
                headers={
                    "Authorization": f"Bearer {config.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": request.model,
                    "input": request.input
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"SiliconFlow API error: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
