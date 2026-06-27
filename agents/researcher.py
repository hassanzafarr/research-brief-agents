"""
Researcher: searches the web for a topic and digests results into notes.
On a retry it reads the Critic's feedback and targets the flagged gaps
instead of repeating the same search.
"""

from graph.state import ResearchState
from utils.llm import get_llm
from utils.search import web_search
from langchain_core.messages import HumanMessage


def researcher_node(state: ResearchState) -> dict:
    topic = state["topic"]
    feedback = state.get("critic_feedback", "")
    loop_count = state.get("research_loops", 0)

    llm = get_llm()

    print(f"\n[Researcher] Pass #{loop_count + 1} on topic: {topic}")

    if feedback:
        # Retry: turn the critic's feedback into a targeted query.
        print(f"[Researcher] Addressing feedback: {feedback}")
        query_prompt = (
            f"Topic: {topic}\n"
            f"A reviewer said our research is missing this: {feedback}\n"
            f"Write ONE concise web search query (just the query text, "
            f"nothing else) that would find the missing information."
        )
    else:
        query_prompt = (
            f"Write ONE concise web search query (just the query text, "
            f"nothing else) to research this topic broadly: {topic}"
        )

    query_response = llm.invoke([HumanMessage(content=query_prompt)])
    search_query = query_response.content.strip()

    raw_results = web_search(search_query)

    # Digest raw results into clean notes instead of storing them as-is.
    digest_prompt = (
        f"Topic: {topic}\n"
        f"Raw search results:\n{raw_results}\n\n"
        f"Summarize the genuinely useful findings from these results as "
        f"3-5 bullet points. Skip anything irrelevant or low-quality."
    )
    digest_response = llm.invoke([HumanMessage(content=digest_prompt)])
    notes = digest_response.content.strip()

    print(f"[Researcher] Found notes:\n{notes}\n")

    return {
        "research_notes": [notes],  # appended via operator.add
        "research_loops": loop_count + 1,
    }
