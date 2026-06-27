"""
Streamlit web UI for the multi-agent research brief generator.

Run locally:
    streamlit run app.py

Deploy:
    Push to GitHub, then connect the repo at https://share.streamlit.io
    (Streamlit Community Cloud). No secrets needed - users paste their own
    API keys in the sidebar, so the app costs the host nothing to run.

Design note: the agent code reads API keys from environment variables at
import time. So this file sets os.environ FROM the user's pasted keys
BEFORE importing the graph - that's why build_graph is imported lazily
inside run_research(), not at the top of the file.
"""

import os
import streamlit as st

st.set_page_config(page_title="Research Brief Generator", page_icon="🔎")


def run_research(topic: str):
    """Stream the graph node-by-node, updating the UI as each agent runs."""
    # Imported here (not at top) so the keys set in os.environ above are
    # already in place when utils/llm.py and utils/search.py build their
    # clients on first import.
    from graph.build import build_graph

    graph = build_graph()
    initial_state = {
        "topic": topic,
        "research_notes": [],
        "critic_feedback": "",
        "is_approved": False,
        "research_loops": 0,
        "final_brief": "",
        "editor_notes": "",
    }

    # Human-readable label for each node as it fires.
    labels = {
        "researcher": "🔍 Researcher — searching and digesting findings",
        "critic": "⚖️ Critic — reviewing research quality",
        "writer": "✍️ Writer — drafting the brief",
        "editor": "✨ Editor — polishing the final brief",
    }

    final_brief = ""
    editor_notes = ""
    progress = st.container()

    # graph.stream yields {node_name: state_update} after each node runs.
    for chunk in graph.stream(initial_state):
        for node_name, update in chunk.items():
            with progress:
                st.write(labels.get(node_name, node_name))
                if node_name == "researcher" and update.get("research_notes"):
                    with st.expander("Research notes from this pass"):
                        st.markdown(update["research_notes"][0])
                if node_name == "critic":
                    verdict = "APPROVED ✅" if update.get("is_approved") else "NEEDS MORE 🔁"
                    st.caption(f"Verdict: {verdict}")
                    if update.get("critic_feedback"):
                        st.caption(f"Feedback: {update['critic_feedback']}")
            if update.get("final_brief"):
                final_brief = update["final_brief"]
            if update.get("editor_notes"):
                editor_notes = update["editor_notes"]

    return final_brief, editor_notes


# ---- UI ----

st.title("🔎 Research Brief Generator")
st.markdown(
    "Give it a topic. Four AI agents — **Researcher → Critic → Writer → "
    "Editor** — collaborate to produce a clean, structured brief. "
    "Built with LangGraph."
)

with st.sidebar:
    st.header("API keys")
    st.caption(
        "Your keys are used only for this session and never stored. "
        "Get them at [console.anthropic.com](https://console.anthropic.com) "
        "and [tavily.com](https://tavily.com)."
    )
    anthropic_key = st.text_input("Anthropic API key", type="password")
    tavily_key = st.text_input("Tavily API key", type="password")

topic = st.text_input(
    "Research topic",
    placeholder="e.g. the impact of AI on small business adoption",
)

if st.button("Generate brief", type="primary"):
    if not anthropic_key or not tavily_key:
        st.error("Enter both API keys in the sidebar first.")
    elif not topic.strip():
        st.error("Enter a topic.")
    else:
        # Inject the user's keys into the environment before the agent
        # modules are imported inside run_research().
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        os.environ["TAVILY_API_KEY"] = tavily_key

        with st.status("Running agents...", expanded=True):
            try:
                brief, notes = run_research(topic.strip())
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                brief, notes = "", ""

        if brief:
            st.subheader("Final brief")
            st.markdown(brief)
            if notes:
                st.caption(f"Editor changed: {notes}")
            st.download_button("Download brief (.md)", brief, "brief.md")
