
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from customize_state.state import State
from customize_state.configuration import llm
from customize_state.memory import memory
from customize_state.tools import tools
graph_builder = StateGraph(State)
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert len(getattr(message, "tool_calls", [])) <= 1
    return {"messages": [message]}  # All state keys (name/birthday) are auto-managed by tool/command update

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=memory)