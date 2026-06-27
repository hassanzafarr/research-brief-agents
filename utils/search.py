"""
Thin wrapper around Tavily so the Researcher agent has a simple function
to call. Tavily is built specifically for AI agents (cleaner results than
scraping raw search engine HTML), and has a free tier that's plenty for
learning/testing.
"""

import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


def web_search(query: str, max_results: int = 5) -> str:
    """
    Runs a web search and returns a formatted string of results.
    Returning a plain string (not raw JSON) keeps things simple for the
    LLM to read - it doesn't need to parse structured data, just read text.

    The Tavily client is built here (per call) rather than at import, so
    the web UI can serve many users each using their own pasted key.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(query=query, max_results=max_results)

    formatted = []
    for i, result in enumerate(response.get("results", []), 1):
        formatted.append(
            f"[Source {i}] {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Content: {result['content']}\n"
        )

    return "\n".join(formatted) if formatted else "No results found."
