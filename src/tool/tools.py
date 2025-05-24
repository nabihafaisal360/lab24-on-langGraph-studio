from langchain_tavily import TavilySearch


tavily_tool = TavilySearch(max_results=2)
tools = [tavily_tool]
