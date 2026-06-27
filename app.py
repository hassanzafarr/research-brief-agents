"""
Streamlit web UI.

    streamlit run app.py

Key handling: a visitor gets one free brief on the host's keys (set as
Streamlit secrets), then is asked to paste their own. Visitor keys are
used right away with no limit. The free-run count is per browser session.
Keys are written to os.environ before the graph runs (imported lazily in
run_research) since the agents read them at call time.
"""

import os
import streamlit as st

st.set_page_config(page_title="Research Brief Generator", page_icon="🔎")


def get_host_keys():
    """Host's own keys from Streamlit secrets, if configured. Both or nothing."""
    try:
        a = st.secrets.get("ANTHROPIC_API_KEY")
        t = st.secrets.get("TAVILY_API_KEY")
        if a and t:
            return a, t
    except Exception:
        pass
    return None, None


def run_research(topic: str):
    """Stream the graph node-by-node, updating the UI as each agent runs."""
    # Imported here (not at top) so the keys set in os.environ are already
    # in place when the LLM/search clients are built.
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

    labels = {
        "researcher": "Researcher: searching and digesting findings",
        "critic": "Critic: reviewing research quality",
        "writer": "Writer: drafting the brief",
        "editor": "Editor: polishing the final brief",
    }

    final_brief = ""
    editor_notes = ""
    progress = st.container()

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


# ---- state ----

if "free_used" not in st.session_state:
    st.session_state.free_used = False

host_anthropic, host_tavily = get_host_keys()
free_available = host_anthropic and host_tavily and not st.session_state.free_used

# ---- UI ----

st.title("Research Brief Generator")
st.markdown(
    "Give it a topic. Four agents (Researcher, Critic, Writer, Editor) "
    "collaborate to produce a structured brief. Built with LangGraph."
)

if free_available:
    st.info(
        "First brief is free. Enter a topic and hit Generate. "
        "After that, add your own API keys in the sidebar to keep going."
    )

with st.sidebar:
    st.header("API keys")
    st.caption(
        "Used only for this session, never stored. Get them at "
        "[console.anthropic.com](https://console.anthropic.com) and "
        "[tavily.com](https://tavily.com) (both have free tiers)."
    )
    anthropic_key = st.text_input("Anthropic API key", type="password")
    tavily_key = st.text_input("Tavily API key", type="password")

topic = st.text_input(
    "Research topic",
    placeholder="e.g. the impact of AI on small business adoption",
)

if st.button("Generate brief", type="primary"):
    user_has_keys = bool(anthropic_key and tavily_key)

    # Decide which keys to use: the visitor's own, else the one free run.
    if user_has_keys:
        use_anthropic, use_tavily, used_free = anthropic_key, tavily_key, False
    elif free_available:
        use_anthropic, use_tavily, used_free = host_anthropic, host_tavily, True
    else:
        use_anthropic = use_tavily = None
        used_free = False

    if not topic.strip():
        st.error("Enter a topic.")
    elif not use_anthropic:
        st.warning(
            "Your free brief is used up. Add your own Anthropic and Tavily "
            "keys in the sidebar to keep generating (both are free to get)."
        )
    else:
        os.environ["ANTHROPIC_API_KEY"] = use_anthropic
        os.environ["TAVILY_API_KEY"] = use_tavily

        with st.status("Running agents...", expanded=True):
            try:
                brief, notes = run_research(topic.strip())
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                brief, notes = "", ""

        if brief:
            if used_free:
                st.session_state.free_used = True
            st.subheader("Final brief")
            st.markdown(brief)
            if notes:
                st.caption(f"Editor changed: {notes}")
            st.download_button("Download brief (.md)", brief, "brief.md")
