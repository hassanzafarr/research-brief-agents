"""
Render the agent graph. Writes graph.mmd (Mermaid source) and graph.png
(via the mermaid.ink API, needs internet).

    python visualize.py
"""

from graph.build import build_graph


def main():
    graph = build_graph()
    g = graph.get_graph()

    mermaid = g.draw_mermaid()
    with open("graph.mmd", "w", encoding="utf-8") as f:
        f.write(mermaid)
    print("Wrote graph.mmd (Mermaid source)")
    print("\n" + mermaid)

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
