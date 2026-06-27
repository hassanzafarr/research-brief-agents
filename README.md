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
```

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
- Visualize the graph with LangGraph's built-in graph drawing
- Add LangSmith tracing to see exact prompts/responses per node
