# Research & Brief Generator (Multi-Agent Orchestration)

A small multi-agent system built with LangGraph to learn the core
concepts of agent orchestration: shared state, conditional routing,
and feedback loops between agents.

## What it does

Give it a topic. Three agents work together to produce a clean,
structured brief:

1. **Researcher** - searches the web and digests findings into notes
2. **Critic** - reviews the notes and decides if they're thorough enough
3. **Writer** - turns approved research into a final brief

If the Critic isn't satisfied, it sends feedback back to the Researcher
for another pass (capped at 3 loops to avoid runaway costs). This loop
is the actual "orchestration" part - the control flow is decided at
runtime based on data, not hardcoded as a straight line.

```
researcher -> critic -> [approved?] -> writer -> end
                |
                +-- [not approved] -> back to researcher
```

## Why this exists

This is a learning project, built to understand agent orchestration
concepts (shared state, conditional edges, loops, safety valves)
hands-on rather than just reading framework docs. See `graph/build.py`
for the actual orchestration logic - that's the file that matters most.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then fill in your API keys
```

You'll need:
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- A Tavily API key ([tavily.com](https://tavily.com), free tier is enough)

## Usage

```bash
python main.py "the impact of agent orchestration on small business AI adoption"
```

Watch the terminal - each agent prints what it's doing, so you can see
the research -> critique -> (maybe loop) -> write flow happen live.

## Project structure

```
agents/
  researcher.py   - searches and digests web findings
  critic.py       - reviews research, decides approve/retry
  writer.py       - synthesizes approved research into a brief
graph/
  state.py        - shared state schema all agents read/write
  build.py        - the actual graph wiring + routing logic
utils/
  llm.py          - shared Claude client config
  search.py       - Tavily search wrapper
main.py           - CLI entry point
visualize.py      - renders the graph to graph.mmd / graph.png
```

## Visualize the graph

See the orchestration as a diagram (nodes + edges, with the conditional
loop drawn as dotted lines):

```bash
python visualize.py
```

Writes `graph.mmd` (Mermaid source, always works) and `graph.png`
(rendered via the mermaid.ink API, needs internet). Offline? Paste
`graph.mmd` into [mermaid.live](https://mermaid.live).

## Tracing with LangSmith

Want to see the exact prompt and response for every node? Turn on
LangSmith tracing - no code changes needed, it's all env vars:

1. Get an API key at [smith.langchain.com](https://smith.langchain.com)
2. In your `.env`, set:
   ```
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_key_here
   LANGCHAIN_PROJECT=research-brief-agents
   ```
3. Run as normal. Each run shows up in LangSmith with a trace tree -
   one span per node (researcher / critic / writer), and inside each
   you can see the full prompt sent to Claude and the raw response.

This is the easiest way to debug WHY the Critic looped, or what the
Researcher actually searched for on a retry.

## Web app (deploy it for others)

There's a Streamlit UI so anyone can use it from a browser - no terminal.

Run locally:

```bash
streamlit run app.py
```

Deploy free on Streamlit Community Cloud:

1. Push this repo to GitHub (already done if you cloned it).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with
   GitHub, and point it at this repo with `app.py` as the entry file.
3. That's it - you get a public URL.

No secrets to configure: each user pastes their own Anthropic + Tavily
keys in the sidebar, so the app costs you nothing to host. Keys are used
only for that session and never stored.

## Things to try once it's running

- Lower `MAX_RESEARCH_LOOPS` in `agents/critic.py` to 1 and watch it
  force-approve after just one pass
- Add a `print(state)` inside any node to see the full state object
  as it flows through the graph
- Try a deliberately vague topic and see if the Critic actually catches
  the gaps, or just rubber-stamps everything (LLM-as-judge isn't perfect)

## Possible next steps

- Swap Tavily for LlamaIndex-based retrieval over a local document set
- Add a fourth agent (fact-checker, tone-checker, etc.)
