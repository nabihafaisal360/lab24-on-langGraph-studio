
from langgraph.graph import StateGraph, START
from basicchatbot.configuration import llm
from basicchatbot.state import State
graph_builder = StateGraph(State)
#the bot replies through this function
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

#starting point of bot
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()
    