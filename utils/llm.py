"""
One shared place to configure the LLM, so every agent uses the same model
and settings. If you want to swap models or tune temperature later,
you only change it here.
"""

import os
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    """
    Build a fresh Claude client, reading the API key from the environment
    at CALL time (not import time). This matters for the web UI: a shared
    server handles many users, each pasting their own key, so we can't bake
    one key into a module-level singleton - that would leak across users.
    """
    return ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        temperature=0.3,  # low-ish: grounded research, not creative flair
        max_tokens=2000,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
