import logging
from typing import Dict, Any
from pdf_mcp.langgraph.graph_builder import build_graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for the graph instance
_graph_instance = None

def run_pipeline(query: str) -> str:
    """
    Runs the query through the LangGraph pipeline.
    
    Args:
        query: The user's query string
        
    Returns:
        Formatted response from either tool execution or prompt execution
    """
    # Log query
    logger.info(f"Processing query: {query}")
    
    # Lazily build and invoke the graph
    global _graph_instance
    if _graph_instance is None:
        logger.info("Initializing LangGraph pipeline for the first time")
        _graph_instance = build_graph()
    
    # Prepare initial state
    initial_state = {
        "query": query,
        "messages": [],
        "final_output": None,
        "branch": "",
        "prompt_name": None,
        "prompt_args": None
    }
    
    # Execute the graph
    result = _graph_instance.invoke(initial_state)
    
    # Extract final output
    final_output = result.get("final_output", "No response generated.")
    
    # Log path taken
    branch = result.get("branch", "unknown")
    prompt_name = result.get("prompt_name")
    
    if branch == "prompt" and prompt_name:
        logger.info(f"Used prompt: {prompt_name}")
    else:
        logger.info("Used tools")
    
    return final_output


def main():
    """Command-line entry point for testing."""
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
