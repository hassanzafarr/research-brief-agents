"""
Graph wiring and routing. Defines the nodes, the edges between them, and
the conditional edge after the Critic that creates the research loop.
"""

from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from agents.researcher import researcher_node
from agents.critic import critic_node
from agents.writer import writer_node
from agents.editor import editor_node


def route_after_critic(state: ResearchState) -> str:
    """Pick the next node based on the Critic's verdict."""
    if state["is_approved"]:
        return "writer"
    return "researcher"  # loop back for another pass


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("critic", critic_node)
    graph.add_node("writer", writer_node)
    graph.add_node("editor", editor_node)

    graph.set_entry_point("researcher")

    graph.add_edge("researcher", "critic")

    # Conditional edge: approve -> writer, otherwise loop back.
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "researcher": "researcher",
            "writer": "writer",
        },
    )

    graph.add_edge("writer", "editor")
    graph.add_edge("editor", END)

    return graph.compile()
