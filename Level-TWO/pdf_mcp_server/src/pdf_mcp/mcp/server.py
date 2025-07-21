from fastmcp import FastMCP
from pdf_mcp.mcp.tools_impl import register_tools
from pdf_mcp.pdf.init_db import index_all_pdfs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server (remove FastAPI completely)
server = FastMCP(name="pdf-mcp-server", version="1.0.0")

# Register tools 
register_tools(server)
# register_prompts(server)

# Index PDFs on startup
try:
    index_result = index_all_pdfs()
    logger.info(f"PDF indexing complete: {index_result}")
except Exception as e:
    logger.error(f"Error indexing PDFs: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting FastMCP server")
    server.run()  
