from fastapi import APIRouter

from app.api.playground.chat import router as chat_router
from app.api.playground.embeddings import router as embeddings_router

# Create main playground router
playground_router = APIRouter()

# Include all playground sub-routers
playground_router.include_router(chat_router)
playground_router.include_router(embeddings_router)
