import os
import sys

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.playground import playground_router
from app.config.agent_config import config
from app.logging_config import configure_logging

configure_logging()

app = FastAPI()

# Define API routes first
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(playground_router)

# Mount static files for assets first
static_files_path = os.path.join(os.path.dirname(__file__), "..", "web", "dist")
if os.path.exists(static_files_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_files_path, "assets")), name="assets")

# Custom SPA handler for client-side routing
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    # Skip API routes
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="Not found")

    # For all other paths, serve index.html for SPA routing
    index_path = os.path.join(static_files_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend not built")

if __name__ == "__main__":
    uvicorn.run("app.app:app", host=config.morn_host, port=config.morn_port, reload=True)
