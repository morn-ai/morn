import logging
import time

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from app.agents.react_agent import MornReActAgent
from app.schemas.chat import ChatRequest

router = APIRouter()
agent = MornReActAgent()

@router.post("/v5/{project_id}/chat")
async def stream_chat(request: Request, chat_request: ChatRequest, project_id: str):
    logging.info(f"Received chat request: {chat_request}")

    async def event_generator():
        logging.info("Starting event generator")
        try:
            start = int(time.time_ns() // 1_000_000)
            async for chunk in agent.stream(chat_request.input, chat_request.thread_id, chat_request.messages, project_id):
                if await request.is_disconnected():
                    logging.info("Client disconnected")
                    break
                logging.info(f"Yielding chunk: {chunk}")
                yield ServerSentEvent(data=chunk, event="message")
            logging.info("Event generator completed")
            end = int(time.time_ns() // 1_000_000)
            logging.info(f"agent cost time: {end - start}")
        except Exception as e:
            logging.error(f"Error in event generator: {str(e)}", exc_info=True)
            yield ServerSentEvent(data=f"Error: {str(e)}", event="error")

    return EventSourceResponse(event_generator())
