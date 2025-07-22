import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.playground import playground_router
from app.config.agent_config import config
from app.logging_config import configure_logging

configure_logging()

app = FastAPI()

# Mount static files from web/dist directory
static_files_path = os.path.join(os.path.dirname(__file__), "..", "web", "dist")
if os.path.exists(static_files_path):
    app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(playground_router)

if __name__ == "__main__":
    uvicorn.run("app.app:app", host=config.morn_host, port=config.morn_port, reload=True)
