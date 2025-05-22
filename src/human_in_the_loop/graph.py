from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from human_in_the_loop.state import State
from human_in_the_loop.configuration import llm
from human_in_the_loop.memory import memory
from human_in_the_loop.tools import tools



graph_builder = StateGraph(State)
llm_with_tools = llm.bind_tools(tools)
def chatbot(state: State):
    valid_messages = [
        msg for msg in state["messages"]
        if getattr(msg, "content", "").strip()
    ]
    if not valid_messages:
        from langchain_core.messages import HumanMessage
        valid_messages = [HumanMessage(content="Hello!")]
    message = llm_with_tools.invoke(valid_messages)
    assert len(getattr(message, "tool_calls", [])) <= 1
    return {"messages": [message]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile(checkpointer=memory)
