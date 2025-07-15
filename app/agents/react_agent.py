import asyncio
import json
import time
from asyncio import Queue
from typing import AsyncGenerator, List

from blockcontent import Block, TextContent

from .callback import StreamingCallbackHandler
from .state_graph import CustomStateGraph
from .util import format_text_block2str
from ..logging_config import configure_logging
from ..schemas.chat import ChatMessage

logger = configure_logging()

class MornReActAgent:
    def __init__(self) -> None:
        logger.info("Initializing IIoT ReAct Agent")
        self.graph = CustomStateGraph().get_compiled_graph()

    async def stream(self, query: str, thread_id: str, messages: List[ChatMessage], project_id: str) -> AsyncGenerator[str, None]:
        try:
            current_timestamp = int(time.time_ns() // 1_000_000)

            if messages is not None and len(messages) > 0:
                user_messages = [{"role": item.role, "content": item.content} for item in messages]
                user_input = {"messages": user_messages}
            else:
                user_input = {"messages": [{"role": "user", "content": query}]}

            # Create a queue for streaming
            queue: Queue = asyncio.Queue()

            # Streaming callback
            streaming_callback = StreamingCallbackHandler(queue)

            # Prepare the input for the agent with all required variables
            config = {
                "configurable": {
                    "timestamp": current_timestamp,
                    "project_id": project_id,
                    "thread_id": thread_id
                },
                "callbacks": [streaming_callback],
                "recursion_limit": 100,
            }

            agent_task = asyncio.create_task(
                self.graph.ainvoke(input=user_input,
                                   config=config,
                                   stream_mode="messages")
            )
            # Stream the output while the agent is running
            while True:
                # 如果 agent 执行完成且 queue 为空，则退出循环
                if agent_task.done() and queue.empty():
                    break
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=0.5)
                    yield item
                except asyncio.TimeoutError:
                    # 超时但 agent 可能还在运行，继续等
                    continue

            # Get the final result
            await agent_task

            yield format_text_block2str("[DONE]")

        except Exception as e:
            error_msg = format_text_block2str(f"错误: {str(e)}")
            logger.error(f"Error in stream_markdown: {str(e)}", exc_info=True)
            yield error_msg
            yield json.dumps(Block(
                type="text",
                text_content=TextContent(
                    text="[DONE]"
                )
            ).to_dict(), ensure_ascii=False)



