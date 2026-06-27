"""
This is the single most important file to understand in the whole project.

In LangGraph, agents don't call each other directly. Instead, they all read
from and write to one shared `state` object that flows through the graph.
Think of it like a clipboard that gets passed from person to person, each
one reading what's on it and adding their own notes before passing it along.

Every node (agent) in the graph receives this state, does its work, and
returns a dict with the fields it wants to UPDATE. LangGraph merges that
into the running state automatically.
"""

from typing import TypedDict, List, Annotated
import operator


class ResearchState(TypedDict):
    # The original topic the user asked about. Set once, never changes.
    topic: str

    # Raw findings gathered by the Researcher agent.
    # Annotated with operator.add means: when multiple updates come in,
    # APPEND to the list instead of overwriting it. This matters because
    # the Researcher might run more than once (after Critic sends it back).
    research_notes: Annotated[List[str], operator.add]

    # Feedback from the Critic agent on the latest research pass.
    # This is what tells the Researcher "you're not done yet, look into X."
    critic_feedback: str

    # Whether the Critic thinks the research is good enough to write from.
    # This is the field the ROUTER reads to decide: loop back, or move on?
    is_approved: bool

    # How many research loops we've done. Critical safety valve -
    # without this, a stubborn Critic could loop forever and burn your API budget.
    research_loops: int

    # The final output from the Writer agent. Empty until the last step.
    final_brief: str
