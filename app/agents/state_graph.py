from copy import deepcopy

from copy import deepcopy

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_core.messages.utils import count_tokens_approximately
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState, create_react_agent
from langgraph.utils.runnable import RunnableCallable
from langmem.short_term import SummarizationNode
from pydantic import SecretStr

from .prompts_loader import load_prompt
from ..config.agent_config import AgentConfig
from ..logging_config import configure_logging
from ..tools.tools import get_all_tools

logger = configure_logging()
model_name = AgentConfig.model_name

class CustomStateGraph:
    def __init__(self):
        tools: list[BaseTool] = get_all_tools()
        logger.info(f"tool len is {len(tools)}, tools are {tools}")

        self.system_prompt = load_prompt("system_prompt")
        self.project_prompt = load_prompt("project_prompt")
        self.human_prompt = load_prompt("human_prompt")

        llm: BaseChatModel = ChatOpenAI(model=model_name,
                                        base_url=AgentConfig.openai_base_url,
                                        api_key=SecretStr(AgentConfig.openai_api_key),
                                        temperature=0,
                                        streaming=True,)
        if len(tools)>0:
            llm = llm.bind_tools(tools=tools)

        checkpointer = InMemorySaver()

        builder = StateGraph(AgentState)

        self.summarization_node:RunnableCallable = SummarizationNode(
            token_counter=count_tokens_approximately,
            model=llm,
            max_tokens=25000,
            max_summary_tokens=20480,
            output_messages_key="llm_input_messages",
        )

        agent = create_react_agent(
            model=llm,
            tools=tools,
            pre_model_hook=self._pre_model_hook,
            checkpointer=checkpointer,
            prompt=self._prompt,
        )

        builder.add_node("agent", agent)
        builder.set_entry_point("agent")

        self.graph = builder.compile(checkpointer=checkpointer)

    def get_compiled_graph(self) -> CompiledStateGraph:
        return self.graph

    def _pre_model_hook(self, state: AgentState, config: RunnableConfig):
        logger.info(f"before summary: {state['messages']}")
        pre_state = deepcopy(state)
        try:
            summarize_state = self.summarization_node.invoke(state, config)
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            return {"llm_input_messages": pre_state['messages']}
        logger.info(f"after summary: {state['messages']}")
        return summarize_state

    def _prompt(self,
                state: AgentState,
                config: RunnableConfig,
                ) -> list[AnyMessage]:
        timestamp = config["configurable"].get("timestamp")
        project_id = config["configurable"].get("project_id")

        msg_list = []
        if self.system_prompt != "":
            msg_list.append(SystemMessage(content=self.system_prompt))
        if self.project_prompt != "":
            msg_list.append(SystemMessage(content=self.project_prompt))
        if self.human_prompt != "":
            human_msg = self.human_prompt.format(timestamp=timestamp, project_id=project_id)
            msg_list.append(HumanMessage(content=human_msg))
        logger.info(f"state msg: {state['messages']}")
        return msg_list + state['messages']
