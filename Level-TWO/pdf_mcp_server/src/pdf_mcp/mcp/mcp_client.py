from langchain_mcp_adapters.client import MultiServerMCPClient
import logging
import asyncio

logger = logging.getLogger(__name__)

class PDFMCPClient:
    """Pure MCP client for tool discovery and execution"""
    
    def __init__(self):
        self.client = None
        self.tools = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize MCP client and discover tools"""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing MCP client connection...")
            
            self.client = MultiServerMCPClient({
                "pdf_mcp": {
                    "command": "python",
                    "args": ["-m", "pdf_mcp.mcp.server"],
                    "transport": "stdio",
                }
            })
            
            logger.info("Discovering tools from MCP server...")
            self.tools = await self.client.get_tools()
            
            if not self.tools:
                raise ValueError("No tools discovered from MCP server")
                
            tool_names = list(self.tools.keys()) if isinstance(self.tools, dict) else [t.name for t in self.tools]
            logger.info(f"Discovered {len(self.tools)} tools: {', '.join(tool_names)}")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"MCP client initialization failed: {e}")
            raise
    
    async def get_tools(self):
        """Get discovered tools for LangGraph binding"""
        if not self._initialized:
            await self.initialize()
        return self.tools
    
    async def health_check(self) -> bool:
        """Check if MCP connection is healthy"""
        try:
            if not self._initialized:
                await self.initialize()
            return self.tools is not None and len(self.tools) > 0
        except Exception:
            return False
    
    async def cleanup(self):
        """Clean up MCP client resources"""
        try:
            self._initialized = False
            logger.info("MCP client cleaned up")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")

# Global MCP client instance
_mcp_client = PDFMCPClient()

async def get_mcp_client() -> PDFMCPClient:
    """Get initialized MCP client instance"""
    if not _mcp_client._initialized:
        await _mcp_client.initialize()
    return _mcp_client

async def cleanup_mcp_client():
    """Cleanup global MCP client"""
    await _mcp_client.cleanup()
