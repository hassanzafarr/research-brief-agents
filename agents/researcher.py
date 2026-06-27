"""
RESEARCHER AGENT

Job: given a topic (and optionally, feedback from a previous critique),
go search the web and gather relevant findings.

This is the simplest agent conceptually, but pay attention to one thing:
it behaves DIFFERENTLY on the first run versus a retry. On a retry, it
needs to read the Critic's feedback and search for the SPECIFIC gaps
that were flagged, not just redo the same generic search. That's what
makes this a real feedback loop instead of a dumb retry.
"""

from graph.state import ResearchState
from utils.llm import llm
from utils.search import web_search
from langchain_core.messages import HumanMessage


def researcher_node(state: ResearchState) -> dict:
    topic = state["topic"]
    feedback = state.get("critic_feedback", "")
    loop_count = state.get("research_loops", 0)

    print(f"\n[Researcher] Pass #{loop_count + 1} on topic: {topic}")

    if feedback:
        # This is a retry. Ask the LLM to turn the critic's feedback
        # into a sharper, more targeted search query.
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

    # Ask the LLM to digest the raw search results into clean notes,
    # rather than dumping unprocessed search junk into the state.
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
        "research_notes": [notes],  # operator.add appends this to the list
        "research_loops": loop_count + 1,
    }
