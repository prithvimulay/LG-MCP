from fastmcp import FastMCP
from pdf_mcp.mcp.tools_impl import register_tools
from pdf_mcp.mcp.prompts_impl import register_prompts
from pdf_mcp.pdf.init_db import index_all_pdfs
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize server
server = FastMCP(name="pdf-mcp-server", version="1.0.0")

# Register tools and prompts
register_tools(server)
register_prompts(server)

# Initialize PDF database
try:
    index_result = index_all_pdfs()
    logging.info(f"PDF indexing complete: {index_result}")
except Exception as e:
    logging.error(f"Error during PDF indexing: {str(e)}")

if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=5001)


