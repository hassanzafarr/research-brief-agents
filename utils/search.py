"""Tavily search wrapper."""

import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


def web_search(query: str, max_results: int = 5) -> str:
    # Returns results as a formatted string for the LLM to read directly.
    # Client is built per call so the web UI can serve users with their
    # own keys.
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
