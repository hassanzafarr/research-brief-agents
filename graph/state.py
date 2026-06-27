"""
Shared state schema. Each node receives this state, does its work, and
returns a dict of the fields it wants to update; LangGraph merges those
into the running state.
"""

from typing import TypedDict, List, Annotated
import operator


class ResearchState(TypedDict):
    # The topic to research. Set once.
    topic: str

    # Findings from the Researcher. operator.add appends across passes
    # instead of overwriting, since the Researcher can run more than once.
    research_notes: Annotated[List[str], operator.add]

    # Critic feedback on the latest pass.
    critic_feedback: str

    # Whether the research is good enough to write from. Read by the router.
    is_approved: bool

    # Number of research loops so far; caps retries.
    research_loops: int

    # Final brief. Written by the Writer, then overwritten by the Editor.
    final_brief: str

    # Editor's one-line note on what it changed.
    editor_notes: str
