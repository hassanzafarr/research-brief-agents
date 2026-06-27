"""Shared LLM config. Change the model or temperature here."""

import os
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    # Read the key at call time, not import time, so the web UI can serve
    # multiple users each with their own key without leaking across them.
    return ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        temperature=0.3,
        max_tokens=2000,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
