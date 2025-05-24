# """Define a custom Reasoning and Action agent.

# Works with a chat model with tool calling support.
# """

# from datetime import UTC, datetime
# from typing import Dict, List, Literal, cast

# from langchain_core.messages import AIMessage
# from langgraph.graph import StateGraph
# from langgraph.prebuilt import ToolNode

# from react_agent.configuration import Configuration
# from react_agent.state import InputState, State
# from react_agent.tools import TOOLS
# from react_agent.utils import load_chat_model

# # Define the function that calls the model


# async def call_model(state: State) -> Dict[str, List[AIMessage]]:
#     """Call the LLM powering our "agent".

#     This function prepares the prompt, initializes the model, and processes the response.

#     Args:
#         state (State): The current state of the conversation.
#         config (RunnableConfig): Configuration for the model run.

#     Returns:
#         dict: A dictionary containing the model's response message.
#     """
#     configuration = Configuration.from_context()

#     # Initialize the model with tool binding. Change the model or add more tools here.
#     model = load_chat_model(configuration.model).bind_tools(TOOLS)

#     # Format the system prompt. Customize this to change the agent's behavior.
#     system_message = configuration.system_prompt.format(
#         system_time=datetime.now(tz=UTC).isoformat()
#     )

#     # Get the model's response
#     response = cast(
#         AIMessage,
#         await model.ainvoke(
#             [{"role": "system", "content": system_message}, *state.messages]
#         ),
#     )

#     # Handle the case when it's the last step and the model still wants to use a tool
#     if state.is_last_step and response.tool_calls:
#         return {
#             "messages": [
#                 AIMessage(
#                     id=response.id,
#                     content="Sorry, I could not find an answer to your question in the specified number of steps.",
#                 )
#             ]
#         }

#     # Return the model's response as a list to be added to existing messages
#     return {"messages": [response]}


# # Define a new graph

# builder = StateGraph(State, input=InputState, config_schema=Configuration)

# # Define the two nodes we will cycle between
# builder.add_node(call_model)
# builder.add_node("tools", ToolNode(TOOLS))

# # Set the entrypoint as `call_model`
# # This means that this node is the first one called
# builder.add_edge("__start__", "call_model")


# def route_model_output(state: State) -> Literal["__end__", "tools"]:
#     """Determine the next node based on the model's output.

#     This function checks if the model's last message contains tool calls.

#     Args:
#         state (State): The current state of the conversation.

#     Returns:
#         str: The name of the next node to call ("__end__" or "tools").
#     """
#     last_message = state.messages[-1]
#     if not isinstance(last_message, AIMessage):
#         raise ValueError(
#             f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
#         )
#     # If there is no tool call, then we finish
#     if not last_message.tool_calls:
#         return "__end__"
#     # Otherwise we execute the requested actions
#     return "tools"


# # Add a conditional edge to determine the next step after `call_model`
# builder.add_conditional_edges(
#     "call_model",
#     # After call_model finishes running, the next node(s) are scheduled
#     # based on the output from route_model_output
#     route_model_output,
# )

# # Add a normal edge from `tools` to `call_model`
# # This creates a cycle: after using tools, we always return to the model
# builder.add_edge("tools", "call_model")

# # Compile the builder into an executable graph
# graph = builder.compile(name="ReAct Agent")

from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from react_agent.configuration import llm_with_tools
from react_agent.tools import tools

import json

# State definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], ...]  # We'll set reducer below

from langgraph.graph.message import add_messages
AgentState.__annotations__["messages"] = Annotated[Sequence[BaseMessage], add_messages]

# tool lookup
tools_by_name = {tool.name: tool for tool in tools}

# Tool node
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

# llm_with_tools node
def call_llm_with_tools(state: AgentState, config: RunnableConfig):
    system_prompt = SystemMessage(
        "You are a helpful AI assistant, please respond to the users query to the best of your ability!"
    )
    response = llm_with_tools.invoke([system_prompt] + state["messages"], config)
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not getattr(last_message, "tool_calls", None):
        return "end"
    else:
        return "continue"

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_llm_with_tools)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)
workflow.add_edge("tools", "agent")
graph = workflow.compile()