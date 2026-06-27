"""
One shared place to configure the LLM, so every agent uses the same model
and settings. If you want to swap models or tune temperature later,
you only change it here.
"""

import os
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0.3,  # low-ish: we want grounded research, not creative flair
    max_tokens=2000,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)
