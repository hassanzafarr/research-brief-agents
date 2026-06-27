"""
CRITIC AGENT

Job: look at everything the Researcher has found SO FAR (all loops combined)
and decide: is this good enough to write a brief from, or is something
important missing?

This is the agent that makes the system a LOOP instead of a straight line.
It's also where you'll see the safety valve in action - even if the Critic
is never satisfied, we cap the loops so the graph can't run forever.
"""

from graph.state import ResearchState
from utils.llm import get_llm
from langchain_core.messages import HumanMessage

MAX_RESEARCH_LOOPS = 3


def critic_node(state: ResearchState) -> dict:
    topic = state["topic"]
    all_notes = "\n\n".join(state["research_notes"])
    loop_count = state["research_loops"]

    print(f"[Critic] Reviewing research after {loop_count} pass(es)")

    # Safety valve: force approval if we've looped too many times,
    # regardless of what the Critic thinks. Prevents infinite loops
    # and runaway API costs.
    if loop_count >= MAX_RESEARCH_LOOPS:
        print(f"[Critic] Hit max loops ({MAX_RESEARCH_LOOPS}), forcing approval")
        return {"is_approved": True, "critic_feedback": ""}

    llm = get_llm()

    review_prompt = (
        f"Topic: {topic}\n"
        f"Research notes gathered so far:\n{all_notes}\n\n"
        f"Is this research thorough enough to write a solid brief on the "
        f"topic? Consider: are there obvious gaps, missing perspectives, "
        f"or unanswered questions a reader would expect covered?\n\n"
        f"Respond in EXACTLY this format:\n"
        f"VERDICT: APPROVED or NEEDS_MORE\n"
        f"FEEDBACK: <if NEEDS_MORE, one specific sentence on what's "
        f"missing. If APPROVED, write 'none'>"
    )

    response = llm.invoke([HumanMessage(content=review_prompt)])
    text = response.content.strip()

    print(f"[Critic] Verdict:\n{text}\n")

    is_approved = "APPROVED" in text.split("FEEDBACK:")[0]
    feedback = ""
    if not is_approved and "FEEDBACK:" in text:
        feedback = text.split("FEEDBACK:")[1].strip()

    return {
        "is_approved": is_approved,
        "critic_feedback": feedback,
    }
