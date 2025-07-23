from fastmcp import FastMCP
from pdf_mcp.mcp.tools_impl import register_tools
from pdf_mcp.pdf.init_db import index_all_pdfs
from pdf_mcp.config.settings import settings
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_server():
    """Initialize FastMCP server with comprehensive tool registration"""
    try:
        server = FastMCP(
            name=settings.mcp_server_name,
            version=settings.mcp_server_version
        )
        
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is required but not configured")
        
        logger.info(f"PDF storage: {settings.pdf_storage_path}")
        logger.info(f"Vector DB: {settings.vector_db_path}")
        
        register_tools(server)
        logger.info("All tools registered successfully with MCP server")
        
        try:
            logger.info("Starting PDF indexing process...")
            index_result = index_all_pdfs()
            
            if index_result and index_result.get('indexed', 0) > 0:
                logger.info(f"PDF indexing completed: {index_result['indexed']} PDFs indexed")
            else:
                logger.warning("No PDFs were indexed")
                
        except Exception as e:
            logger.error(f"PDF indexing failed: {str(e)}")
            logger.info("Server will continue - PDFs can be indexed on-demand")

        logger.info("FastMCP server initialization complete")
        return server
        
    except Exception as e:
        logger.error(f"Server initialization failed: {e}")
        raise

async def run_server_async():
    """Async server runner for integration with async applications"""
    server = initialize_server()
    logger.info("Starting FastMCP server with stdio transport (async)")
    await server.run_async(transport="stdio")

def main():
    """Main entry point for standalone server execution"""
    try:
        server = initialize_server()
        logger.info("Starting FastMCP server with stdio transport")
        server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise

if __name__ == "__main__":
    main()
