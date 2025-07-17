import logging
from typing import List, TypedDict, Annotated

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from app.agents.prompt_loader import load_prompt
from app.config.agent_config import config


class AgentState(TypedDict):
    """State for the agent"""
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]


class MornReActAgent:
    def __init__(self):
        logging.info("Initializing morn Agent with LangGraph")
        self.system_prompt = load_prompt("system_prompt")

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=config.openai_model,
            api_key=config.openai_api_key,
            base_url=config.openai_api_base,
        )

        # Create the graph
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> CompiledStateGraph:
        """Create LangGraph workflow"""
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", self._agent_node)

        workflow.add_edge(START, "agent")

        workflow.add_edge("agent", END)

        return workflow.compile()

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

    def process_message(self, user_input: str) -> str:
        """Process user input using LangGraph workflow"""
        # Initialize state
        state = {
            "messages": [HumanMessage(content=user_input)],
        }

        # Run the workflow
        result = self.workflow.invoke(state)

        # Get the final response
        final_message = result["messages"][-1]
        return final_message.content
