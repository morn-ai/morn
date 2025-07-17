import logging
import uuid
from typing import List, TypedDict, Annotated, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph, END

from app.agents.prompt_loader import load_prompt
from app.config.agent_config import config
from app.logging_config import configure_logging
from app.schemas.chat import ChatCompletionChunk

configure_logging()

class AgentState(TypedDict):
    """State for the agent"""
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]


class MornReActAgent:
    def __init__(self):
        logging.info("Initializing morn Agent with LangGraph")
        self.system_prompt = load_prompt("system_prompt")
        self.checkpointer = InMemorySaver()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=config.openai_model,
            api_key=config.openai_api_key,
            base_url=config.openai_api_base,
        )

        # Create the graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._agent_node)
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
        self.workflow = workflow.compile(checkpointer=self.checkpointer)

    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent node - processes the conversation"""
        messages = state["messages"]

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{self.system_prompt}"),
            MessagesPlaceholder(variable_name="messages"),
        ])

        # Create the agent
        agent = prompt | self.llm

        # Run the agent
        response = agent.invoke({
            "messages": messages,
        })

        # Add the response to messages
        new_messages = messages + [response]

        return {
            **state,
            "messages": new_messages
        }

    def process_message(self, user_input: str, thread_id: Optional[str] = None) -> str:
        state, thread_id = self.get_history_messages(thread_id, user_input)

        # Run the workflow with thread_id
        result = self.workflow.invoke(state, config={"configurable": {"thread_id": thread_id}})

        # Get the final response
        final_message = result["messages"][-1]
        return final_message.content

    async def stream_message(self, user_input: str, thread_id: Optional[str] = None):
        """Stream the response from the agent"""
        state, thread_id = self.get_history_messages(thread_id, user_input)
        async for chunk in self._stream(state, running_config={"configurable": {"thread_id": thread_id}}):
            yield chunk

    def get_history_messages(self, thread_id, user_input):
        """Process user input using LangGraph workflow with thread support"""
        # Generate thread_id if not provided
        if thread_id is None:
            thread_id = str(uuid.uuid4())
            logging.info(f"Generated new thread_id: {thread_id}")
        # Initialize state with new message
        new_message = HumanMessage(content=user_input)
        # Get existing state from checkpointer or create new one
        try:
            # Try to get existing thread state
            existing_state = self.checkpointer.get(thread_id)
            if existing_state:
                # Add new message to existing conversation
                messages = existing_state["messages"] + [new_message]
                logging.info(f"Continuing conversation in thread {thread_id} with {len(messages)} messages")
            else:
                # Start new conversation
                messages = [new_message]
                logging.info(f"Starting new conversation in thread {thread_id}")
        except Exception as e:
            # If there's any error getting state, start fresh
            logging.warning(f"Error getting thread state for {thread_id}: {e}. Starting fresh.")
            messages = [new_message]
        state = {
            "messages": messages,
        }
        return state, thread_id

    async def _stream(self, state: AgentState, running_config: dict):
        """Stream the response from the agent"""
        async for (chunk_or_message, metadata) in self.workflow.astream(input=state, config=running_config, stream_mode="messages"):
            try:
                logging.info(f"chunk: {chunk_or_message}")
                if isinstance(chunk_or_message, AIMessageChunk):
                    chat_completion_chunk = ChatCompletionChunk(id=str(uuid.uuid4()),
                                                                model=config.openai_model,
                                                                choices=[{
                                                                    "delta": {
                                                                        "content": chunk_or_message.content
                                                                    },
                                                                    "finish_reason": None
                                                                }],
                                                                created=0, )
                    yield chat_completion_chunk.model_dump_json()
            except Exception as e:
                logging.error(f"Error processing chunk: {e}")

    def get_thread_messages(self, thread_id: str) -> List[BaseMessage]:
        """Get all messages for a specific thread"""
        try:
            state = self.checkpointer.get(thread_id)
            if state:
                return state["messages"]
            return []
        except Exception as e:
            logging.warning(f"Error getting messages for thread {thread_id}: {e}")
            return []

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and its conversation history"""
        try:
            self.checkpointer.delete(thread_id)
            logging.info(f"Deleted thread {thread_id}")
            return True
        except Exception as e:
            logging.error(f"Error deleting thread {thread_id}: {e}")
            return False

    def list_threads(self) -> List[str]:
        """List all available thread IDs"""
        try:
            return list(self.checkpointer.list())
        except Exception as e:
            logging.error(f"Error listing threads: {e}")
            return []
