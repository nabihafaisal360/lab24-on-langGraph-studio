# """This module provides example tools for web scraping and search functionality.

# It includes a basic Tavily search function (as an example)

# These tools are intended as free examples to get started. For production use,
# consider implementing more robust and specialized tools tailored to your needs.
# """

# from typing import Any, Callable, List, Optional, cast

# from langchain_tavily import TavilySearch  # type: ignore[import-not-found]

# from react_agent.configuration import Configuration


# async def search(query: str) -> Optional[dict[str, Any]]:
#     """Search for general web results.

#     This function performs a search using the Tavily search engine, which is designed
#     to provide comprehensive, accurate, and trusted results. It's particularly useful
#     for answering questions about current events.
#     """
#     configuration = Configuration.from_context()
#     wrapped = TavilySearch(max_results=configuration.max_search_results)
#     return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))


# TOOLS: List[Callable[..., Any]] = [search]
#from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_weather(location: str):
    """Call to get the weather from a specific location."""
    # Simulated logic (replace with real API if desired)
    if any([city in location.lower() for city in ["sf", "san francisco"]]):
        return "It's sunny in San Francisco, but you better look out if you're a Gemini 😈."
    else:
        return f"I am not sure what the weather is in {location}"

tools = [get_weather]               