import json
import logging

from blockcontent import Block, TextContent, ChartContent
from langchain_core.messages import ToolMessage, AnyMessage, AIMessage, ToolCall

from ..logging_config import configure_logging

tool_request_markdown = """
开始调用工具：
| 字段   | 值                     |
|----------------|-----------------------------------------------|
| 工具调用ID   | {id} |
| 工具名称      | {name}                                  |
| 参数           | {args}       |
"""

tool_response_markdown = """
**工具ID**: {id}
**工具名称**: {name}
**调用结果**：{status}
**内容**：
{result}
"""

logger = configure_logging()

def format_text_block2str(text: str | dict) -> str:
    if isinstance(text, dict):
        text = json.dumps(text, ensure_ascii=False)
    return json.dumps(Block(
            type="text",
            text_content=TextContent(
                text=text
            )
        ).to_dict(), ensure_ascii=False)

def format_chart_block2str(chart_type: str, labels: list, datasets: list) -> str:
    """Helper method to yield a chart block."""
    block = Block(
        type="chart",
        chart_content=ChartContent(
            chart_type=chart_type,
            labels=labels,
            datasets=datasets
        )
    )
    return json.dumps(block.to_dict(), ensure_ascii=False)

def format2block(text: str | dict) -> Block:
    if isinstance(text, dict):
        text = json.dumps(text, ensure_ascii=False)
    return Block(
            type="text",
            text_content=TextContent(
                text=text
            ))

def is_json(json_str: str) -> bool:
    try:
        json.loads(json_str)  # 尝试解析字符串
        return True
    except json.JSONDecodeError:
        return False

def process_message(message: AnyMessage) -> Block:
    # AIMessage: 调用工具
    if isinstance(message, AIMessage):
        tool_calls: list[ToolCall] = message.tool_calls
        # 工具调用
        if tool_calls is not None and len(tool_calls) > 0:
            tool_call = tool_calls[0]

            tool_result = tool_request_markdown.format(
                id=tool_call['id'],
               name=tool_call['name'],
               args=tool_call['args']
            )

            return format2block(message.content + '\n' + tool_result)
        else:
            return format2block(message.content)

    # ToolMessage: 调用结果
    elif isinstance(message, ToolMessage):
        tool_result = message.content
        tool_call_id = message.tool_call_id
        tool_name = message.name
        tool_status = message.status
        if is_json(tool_result):
            tool_result = json.loads(tool_result)
        logging.info(f"too_name: {tool_name}, tool_status: {tool_status}, tool_result: {tool_result}")
        if tool_name == "format_chart":
            logging.info("Formatting chart")
            if isinstance(tool_result, dict) and "type" in tool_result and "content" in tool_result:
                content = tool_result["content"]
                for dataset in content["datasets"]:
                    if "data" in dataset:
                        data = list(map(lambda x : float(x), dataset["data"]))
                        dataset["data"] = data

            return Block(type="chart",
                         chart_content=ChartContent(chart_type=content.get("type", "line"),
                    labels=content.get("labels", []),
                    datasets=content.get("datasets", []))
            )

        tool_result = tool_response_markdown.format(
            id=tool_call_id,
            name=tool_name,
            result= f'```json\n{json.dumps(tool_result, indent=4, ensure_ascii=False)}\n```' if isinstance(tool_result, dict) else tool_result,
            status=tool_status
        )
        return format2block(tool_result)
    else:
        return Block(
            type="text",
            text_content=TextContent(
                text=message.content
            )
        )
