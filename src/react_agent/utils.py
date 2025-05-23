# """Utility & helper functions."""

# from langchain.chat_models import init_chat_model
# from langchain_core.language_models import BaseChatModel
# from langchain_core.messages import BaseMessage


# def get_message_text(msg: BaseMessage) -> str:
#     """Get the text content of a message."""
#     content = msg.content
#     if isinstance(content, str):
#         return content
#     elif isinstance(content, dict):
#         return content.get("text", "")
#     else:
#         txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
#         return "".join(txts).strip()


# def load_chat_model(fully_specified_name: str) -> BaseChatModel:
#     """Load a chat model from a fully specified name.

#     Args:
#         fully_specified_name (str): String in the format 'provider/model'.
#     """
#     provider, model = fully_specified_name.split("/", maxsplit=1)
#     return init_chat_model(model, model_provider=provider)
import json
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from react_agent.tools import tools
from react_agent.state import AgentState
from react_agent.configuration import llm

tools_by_name = {tool.name: tool for tool in tools}


# Define our tool node
def tool_node(state: AgentState):
    outputs = []
    for tool_call in state["messages"][-1].tool_calls:
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            ToolMessage(
                content=json.dumps(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}


# Define the node that calls the model
def call_model(
    state: AgentState,
    config: RunnableConfig,
):
    # this is similar to customizing the create_react_agent with 'prompt' parameter, but is more flexible
    system_prompt = SystemMessage(
        "You are a helpful AI assistant, please respond to the users query to the best of your ability!"
    )
    response = llm.invoke([system_prompt] + state["messages"], config)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the conditional edge that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"