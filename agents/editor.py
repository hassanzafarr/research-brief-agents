"""
EDITOR AGENT

Job: take the Writer's draft brief and do a final polish pass - tighten the
tone, fix awkward phrasing, enforce consistency, and cut any remaining bloat.

This is the LAST agent in the pipeline. The Writer turns research into a
structured draft; the Editor makes that draft read like a human wrote it on
a good day. It only ever runs once, after the Writer has signed off, so it
doesn't loop - it's a straight pass-through that overwrites `final_brief`
with the cleaned-up version.

Swap the prompt below to change what this agent enforces (e.g. a fact-checker
would instead compare claims against the research notes, a tone-checker would
enforce a target voice). The wiring in graph/build.py stays the same.
"""

from graph.state import ResearchState
from utils.llm import llm
from langchain_core.messages import HumanMessage


def editor_node(state: ResearchState) -> dict:
    topic = state["topic"]
    draft = state["final_brief"]

    print(f"[Editor] Polishing brief on: {topic}")

    edit_prompt = (
        f"Topic: {topic}\n"
        f"Draft brief:\n{draft}\n\n"
        f"You are a sharp copy editor. Rewrite the draft to improve tone, "
        f"clarity, and flow WITHOUT adding new facts or claims. Keep the "
        f"same structure (intro, key points, takeaway). Fix awkward "
        f"phrasing, cut filler, and make the voice confident and clean.\n\n"
        f"Then add ONE final line starting with 'EDITOR_NOTE:' summarizing "
        f"what you changed in a sentence."
    )

    response = llm.invoke([HumanMessage(content=edit_prompt)])
    text = response.content.strip()

    # Split the polished brief from the editor's note about what changed.
    note = ""
    if "EDITOR_NOTE:" in text:
        polished, note = text.split("EDITOR_NOTE:", 1)
        polished = polished.strip()
        note = note.strip()
    else:
        polished = text

    print(f"[Editor] Done. {note}\n")

    return {
        "final_brief": polished,
        "editor_notes": note,
    }
