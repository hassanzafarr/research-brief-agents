"""
THE GRAPH

This file is the actual "orchestrator." Everything else (agents, state)
is just supporting cast. This is where you define:
  1. What nodes (agents) exist
  2. How they connect (edges)
  3. Where there's a DECISION point that can route to different places
     depending on state (conditional edges) - this is the difference
     between a simple chain and real orchestration.

Read this file top to bottom and you'll understand the whole system's
control flow without needing to read any agent's internals.
"""

from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from agents.researcher import researcher_node
from agents.critic import critic_node
from agents.writer import writer_node
from agents.editor import editor_node


def route_after_critic(state: ResearchState) -> str:
    """
    This function is the ROUTER. After the Critic runs, LangGraph calls
    this function with the current state, and whatever string it returns
    determines which node runs next.

    This is the single most important concept in agent orchestration:
    the NEXT STEP IS DECIDED AT RUNTIME based on data, not hardcoded
    in advance. A plain chain (A -> B -> C) can't do this.
    """
    if state["is_approved"]:
        return "writer"
    else:
        return "researcher"  # loop back for another pass


def build_graph():
    graph = StateGraph(ResearchState)

    # Register each agent as a node in the graph.
    graph.add_node("researcher", researcher_node)
    graph.add_node("critic", critic_node)
    graph.add_node("writer", writer_node)
    graph.add_node("editor", editor_node)

    # The entry point: every run starts at the researcher.
    graph.set_entry_point("researcher")

    # Researcher always hands off to Critic. This is a plain edge,
    # no decision involved.
    graph.add_edge("researcher", "critic")

    # Critic's output determines what happens next - this is the
    # conditional edge that creates the loop.
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "researcher": "researcher",  # loop back
            "writer": "writer",          # move forward
        },
    )

    # Writer drafts, then hands off to the Editor for a final polish pass.
    # Plain edges - no decision, the brief always goes through the Editor.
    graph.add_edge("writer", "editor")

    # Once the Editor is done, the graph ends.
    graph.add_edge("editor", END)

    return graph.compile()
