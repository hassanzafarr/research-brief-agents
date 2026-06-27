"""
Draw the agent graph using LangGraph's built-in graph rendering.

Run:
    python visualize.py

Outputs two files in the project root:
    graph.mmd  - Mermaid source text (always works, no internet needed)
    graph.png  - rendered PNG (needs internet: uses the mermaid.ink API)

The PNG step calls an external service to render the Mermaid diagram.
If you're offline or it fails, you still get graph.mmd, which you can
paste into https://mermaid.live to see the diagram.
"""

from graph.build import build_graph


def main():
    graph = build_graph()
    g = graph.get_graph()

    # Mermaid source - pure text, no dependencies, never fails.
    mermaid = g.draw_mermaid()
    with open("graph.mmd", "w", encoding="utf-8") as f:
        f.write(mermaid)
    print("Wrote graph.mmd (Mermaid source)")
    print("\n" + mermaid)

    # PNG render - calls the mermaid.ink API, needs internet.
    try:
        png = g.draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png)
        print("Wrote graph.png")
    except Exception as e:
        print(f"PNG render skipped ({e}).")
        print("Paste graph.mmd into https://mermaid.live to view it.")


if __name__ == "__main__":
    main()
