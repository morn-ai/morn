import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette import EventSourceResponse

from app.agents.react_agent import MornReActAgent
from app.api.auth import require_auth
from app.schemas.auth import TokenData
from app.schemas.chat import ChatRequest

router = APIRouter()

agent = MornReActAgent()

@router.post("/api/v1/chat")
async def chat(
        request: ChatRequest,
        current_user: Annotated[TokenData, Depends(require_auth)]
):
    logging.info(f"receive chat request: {request}")

    async def event_generator():
        try:
            logging.info("Starting event generator")

            # Process the message using our LangGraph agent
            # Get the last message from the request
            if request.messages:
                last_message = request.messages[-1].content
                async for chunk in agent.stream_message(last_message, thread_id=request.thread_id):
                    yield chunk
            else:
                yield { "event": "message", "data": "No message provided."}

            # Send completion signal
            yield {
                "event": "message",
                "data": "[DONE]"
            }

        except Exception as e:
            logging.error(f"Error in chat event generator: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())


@router.get("/api/v1/threads")
async def list_threads(
        current_user: Annotated[TokenData, Depends(require_auth)]
):
    """List all available threads for the current user"""
    try:
        threads = agent.list_threads()
        return {"threads": threads}
    except Exception as e:
        logging.error(f"Error listing threads: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/threads/{thread_id}/messages")
async def get_thread_messages(
        thread_id: str,
        current_user: Annotated[TokenData, Depends(require_auth)]
):
    """Get all messages for a specific thread"""
    try:
        messages = agent.get_thread_messages(thread_id)
        # Convert messages to serializable format
        serialized_messages = []
        for msg in messages:
            serialized_messages.append({
                "type": msg.__class__.__name__,
                "content": msg.content,
                "additional_kwargs": msg.additional_kwargs
            })
        return {"thread_id": thread_id, "messages": serialized_messages}
    except Exception as e:
        logging.error(f"Error getting thread messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/api/v1/threads/{thread_id}")
async def delete_thread(
        thread_id: str,
        current_user: Annotated[TokenData, Depends(require_auth)]
):
    """Delete a thread and its conversation history"""
    try:
        success = agent.delete_thread(thread_id)
        if success:
            return {"message": f"Thread {thread_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Thread not found")
    except Exception as e:
        logging.error(f"Error deleting thread: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
