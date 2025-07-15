import asyncio
import json
import os

from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from ..config.agent_config import AgentConfig
from ..logging_config import configure_logging

logger = configure_logging()

if os.path.exists(AgentConfig.morn_mcp_conf_file):
    with open(AgentConfig.morn_mcp_conf_file, "r", encoding="utf-8") as f:
        try:
            mcp_conf = json.load(f)
            logger.info(f"load mcp conf from {AgentConfig.morn_mcp_conf_file}")
            client = MultiServerMCPClient(mcp_conf)
        except Exception as e:
            logger.error(f"failed to load mcp conf from {AgentConfig.morn_mcp_conf_file}: {e}")

def get_all_tools() -> list[StructuredTool]:
    """
    Get all available tools.

    Returns:
        List of all available tools
    """
    tools = []

    # add MCP tools
    try:
        mcp_tools = asyncio.run(client.get_tools())
        tools.extend(mcp_tools)
    except Exception as ex:
        logger.error(f"failed to get mcp tools: {ex}")

    return tools
