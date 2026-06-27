"""
CLI entry point.

Usage:
    python main.py "your research topic here"
"""

import sys
from graph.build import build_graph


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py "your topic here"')
        sys.exit(1)

    topic = " ".join(sys.argv[1:])

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

    print(f"{'='*60}")
    print(f"Starting research on: {topic}")
    print(f"{'='*60}")

    final_state = graph.invoke(initial_state)

    print(f"\n{'='*60}")
    print("FINAL BRIEF")
    print(f"{'='*60}\n")
    print(final_state["final_brief"])

    if final_state.get("editor_notes"):
        print(f"\n[Editor changed] {final_state['editor_notes']}")


if __name__ == "__main__":
    main()
