import asyncio
import logging
from pdf_mcp.langgraph.graph_builder import build_graph
from pdf_mcp.mcp.mcp_client import get_mcp_client

logger = logging.getLogger(__name__)

_graph_instance = None

async def run_pipeline_async(query: str) -> str:
    """Run pipeline async"""
    global _graph_instance
    if _graph_instance is None:
        logger.info("Initializing LangGraph pipeline")
        
        # Ensure MCP client is connected
        client = await get_mcp_client()
        await client.connect()
        logger.info("MCP client connected")
        
        _graph_instance = build_graph()
        logger.info("LangGraph pipeline initialized")

    initial_state = {
        "query": query,
        "messages": [],
        "final_output": None,
        "branch": "",
        "tool_name": None,
        "tool_args": None
    }

    try:
        result = await _graph_instance.ainvoke(initial_state)  # Use ainvoke for async
        return result.get("final_output", "No response generated")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return f"Error: {str(e)}"

def run_pipeline(query: str) -> str:
    """Sync wrapper for async pipeline"""
    return asyncio.run(run_pipeline_async(query))
