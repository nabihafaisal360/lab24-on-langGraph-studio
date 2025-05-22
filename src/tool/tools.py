from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.types import interrupt
tavily_tool = TavilySearch(max_results=2)
tools = [tavily_tool]
