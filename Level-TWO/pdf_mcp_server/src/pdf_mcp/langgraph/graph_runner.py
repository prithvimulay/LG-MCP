def run_pipeline(query: str):
    from pdf_mcp.langgraph.graph_builder import build_graph
    graph = build_graph()
    result = graph.invoke({"query": query})
    return result["final_output"]


def main():
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage: python -m pdf_mcp.langgraph.graph_runner \"Your query\"")
        return

    query = " ".join(sys.argv[1:])
    print(f"🔍 Query: {query}")
    start_time = time.time()

    try:
        result = run_pipeline(query)
        print(f"\n📝 Result:\n{result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    duration = time.time() - start_time
    print(f"\n⏱️ Completed in {duration:.2f}s")


if __name__ == "__main__":
    main()
