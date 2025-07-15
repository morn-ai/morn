import asyncio
import json
import os
from typing import Optional, Union, Any, TypedDict

from blockcontent import Block, ChartContent, TextContent
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.outputs import GenerationChunk, LLMResult, ChatGenerationChunk
from datetime import datetime

from .util import process_message
from ..logging_config import configure_logging

logger = configure_logging()

class TimeMetrics(TypedDict):
    llm: Optional[datetime]
    tool: Optional[datetime]

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, queue: asyncio.Queue):
        self.time_metrics: TimeMetrics = TimeMetrics(llm=None, tool=None)
        self.queue = queue
        logger.info("Initializing StreamingCallbackHandler")

    async def _yield_text(self, text: str):
        """Helper method to yield a text token."""
        try:
            await self.queue.put(text)
        except Exception as e:
            logger.error(f"Error yielding text: {str(e)}")

    async def _yield_block(self, block: Block):
        """Helper method to yield a block."""
        try:
            await self.queue.put(json.dumps(block.to_dict(), ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error yielding block: {str(e)}")

    async def _yield_chart_block(self, chart_type: str, labels: list, datasets: list):
        """Helper method to yield a chart block."""
        try:
            block = Block(
                type="chart",
                chart_content=ChartContent(
                    chart_type=chart_type,
                    labels=labels,
                    datasets=datasets
                )
            )
            await self._yield_block(block)
        except Exception as e:
            logger.error(f"Error yielding chart block: {str(e)}")

    async def on_llm_new_token(self, token: str, chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]],**kwargs):
        """Run when LLM generates a new token."""
        logger.info(f"on_llm_new_token: {token}, chunk={chunk}, kwargs={kwargs}")
        # 使用工具的思考内容在tool_call_chunks中
        if token == '':
            tool_chunks_content = ""
            chunk_message = chunk.message
            tool_chunks = chunk_message.tool_call_chunks
            if tool_chunks is not None:
                for chunk in tool_chunks:
                    tool_chunks_content += chunk['args']
                await self._yield_text(tool_chunks_content)
        else:
            await self._yield_text(token)

    async def on_llm_end(self, response: LLMResult, **kwargs):
        logger.info(f"llm cost: {datetime.now() - self.time_metrics['llm']}")
        """Run when LLM ends running."""
        logger.info(f"on_llm_end response: {response}, kwargs={kwargs}")

        for generation in response.generations:
            for generation_info in generation:
                message = generation_info.message
                if isinstance(message, BaseMessage):
                    await self._yield_block(process_message(message))
                # token统计开关
                if 'TOKEN_COUNT' in os.environ:
                    await self._yield_block(Block(
                        type="text",
                        text_content=TextContent(
                            text=json.dumps(message.usage_metadata)
                        ))
                    )

    async def on_llm_error(self, error: BaseException, **kwargs):
        """Run when LLM errors."""
        logger.error(f"on_llm_error: {error}, kwargs={kwargs}")
        block = Block(
            type="text",
            text_content=TextContent(text=f"LLM错误: {str(error)}")
        )
        await self._yield_block(block)

    async def on_chain_error(self, error: BaseException, **kwargs):
        logger.error(f"on_chain_error: {error}, kwargs={kwargs}")
        block = Block(
            type="text",
            text_content=TextContent(text=f"处理链错误: {str(error)}")
        )
        await self._yield_block(block)

    async def on_agent_action(self, action: AgentAction, **kwargs):
        logger.info(f"on_agent_action: {action}, attrs={dir(action)}, kwargs={kwargs}")

        # Extract thought and action information
        thought = getattr(action, 'log', '')
        if not thought and hasattr(action, 'tool_input'):
            thought = f"思考: {action.tool_input}"

        tool = getattr(action, 'tool', '')
        tool_input = getattr(action, 'tool_input', '')

        # Combine thought and action into a single message
        message_parts = []
        if thought:
            message_parts.append(f"思考过程: {thought}")
        if tool:
            message_parts.append(f"执行工具: {tool}\n输入参数: {tool_input}")

        if message_parts:
            block = Block(
                type="text",
                text_content=TextContent(text="\n".join(message_parts))
            )
            await self._yield_block(block)

    async def on_agent_finish(self, finish: AgentFinish, **kwargs):
        logger.info(f"on_agent_finish: {finish}, kwargs={kwargs}")
        if hasattr(finish, 'return_values'):
            output = finish.return_values.get('output', '')
            block = Block(
                type="text",
                text_content=TextContent(text=output)
            )
            await self._yield_block(block)
        else:
            logger.warning(f"Finish object has no return_values attribute. Available attrs: {dir(finish)}")

    async def on_tool_end(self, output: Any, **kwargs):
        logger.info(f"tool cost: {datetime.now() - self.time_metrics['tool']}")
        logger.info(f"on_tool_end: {output}, type={type(output).__name__}, kwargs={kwargs}")

        # handle tool message
        if isinstance(output, ToolMessage):
            await self._yield_block(process_message(output))
            return

        # Handle regular text output
        formatted_output = output
        if isinstance(output, str):
            try:
                obs_json = json.loads(output)
                formatted_output = json.dumps(obs_json, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                pass

        block = Block(
            type="text",
            text_content=TextContent(text=f"执行结果: {formatted_output}")
        )
        await self._yield_block(block)


    async def on_tool_error(self, error: BaseException, **kwargs):
        """Run when tool errors."""
        logger.error(f"on_tool_error: {error}, kwargs={kwargs}")
        block = Block(
            type="text",
            text_content=TextContent(text=f"工具执行错误: {str(error)}")
        )
        await self._yield_block(block)

    # RetrieverManagerMixin, on_retriever_end, on_retriever_error

    # CallbackManagerMixin, on_llm_start, on_chat_model_start, on_retriever_start, on_chain_start, on_tool_start

    async def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs):
        self.time_metrics['llm'] = datetime.now()
        """Run when LLM starts running."""
        if prompts:
            prompt_0_preview = prompts[0][:100].replace('\n', ' ') + '...'
            other_prompts = prompts[1:]
        else:
            prompt_0_preview = 'N/A'
            other_prompts = []

        logger.info(f"on_llm_start: {serialized}, prompt[0]={prompt_0_preview}, prompts[1:]={other_prompts}, kwargs={kwargs}")

    async def on_chain_start(self, serialized: dict[str, Any], inputs: dict[str, Any], **kwargs):
        logger.debug(f"on_chain_start: {serialized}, inputs={inputs}, kwargs={kwargs}")

    async def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs):
        self.time_metrics['tool'] = datetime.now()
        # agent_action also record the event
        logger.debug(f"on_tool_start: {serialized}, input_str={input_str}, kwargs={kwargs}")
        await self._yield_text(f"on_tool_start: {serialized}, input_str={input_str}, kwargs={kwargs}")

    # RunManagerMixin, on_text, on_retry, on_custom_event

    async def on_text(self, text: str, **kwargs):
        logger.info(f"on_text: {text}, kwargs={kwargs}")
        await self._yield_text(text)
