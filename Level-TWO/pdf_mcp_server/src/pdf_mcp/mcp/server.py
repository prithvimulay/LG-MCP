from fastmcp import FastMCP
from fastapi import FastAPI
from pdf_mcp.mcp.tools_impl import register_tools
from pdf_mcp.mcp.prompts_impl import register_prompts
from pdf_mcp.pdf.init_db import index_all_pdfs
from pdf_mcp.langgraph.graph_runner import run_pipeline
import logging
from fastapi.responses import JSONResponse
import uvicorn

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app directly - simpler and more reliable approach
app = FastAPI(title="PDF MCP Server")

# Initialize FastMCP server
server = FastMCP(name="pdf-mcp-server", version="1.0.0")
register_tools(server)
register_prompts(server)

# Mount FastMCP server to the /mcp endpoint
app.mount("/mcp", server)

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "healthy"})

# Query endpoint
@app.post("/query")
async def query(payload: dict):
    query = payload.get("query")
    if not query:
        return JSONResponse(status_code=400, content={"error": "Query is required"})

    logging.info(f"Processing query via LangGraph: {query}")
    try:
        # Use enhanced graph pipeline with conditional tool/prompt selection
        result = run_pipeline(query)
        return JSONResponse(status_code=200, content={"response": result})
    except Exception as e:
        logging.error(f"Query error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Index PDFs on startup
try:
    index_result = index_all_pdfs()
    logging.info(f"PDF indexing complete: {index_result}")
except Exception as e:
    logging.error(f"Error indexing PDFs: {str(e)}")

def run_server(host="0.0.0.0", port=5001):
    logging.info(f"Starting MCP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()