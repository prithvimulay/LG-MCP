def run_pipeline(query: str):
    from pdf_mcp.langgraph.graph_builder import build_graph
    graph = build_graph()
    result = graph.invoke({"query": query})
    return result["final_output"]
