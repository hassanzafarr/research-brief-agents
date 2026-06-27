"""
Editor: final polish pass over the Writer's draft. Improves tone, clarity,
and flow without adding new claims, and overwrites final_brief.
"""

from graph.state import ResearchState
from utils.llm import get_llm
from langchain_core.messages import HumanMessage


def editor_node(state: ResearchState) -> dict:
    topic = state["topic"]
    draft = state["final_brief"]

    llm = get_llm()

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

    # Separate the polished brief from the editor's note.
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
