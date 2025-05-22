from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.types import interrupt
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    answer = human_response.get("data", "").strip()
    if not answer:
        answer = "Sorry, no feedback was provided by the human."
    return answer
tavily_tool = TavilySearch(max_results=2)
tools = [tavily_tool, human_assistance]
