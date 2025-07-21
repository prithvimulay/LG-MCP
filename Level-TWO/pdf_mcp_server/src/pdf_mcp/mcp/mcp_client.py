import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logging

logger = logging.getLogger(__name__)

class PDFMCPClient:
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.session: Optional[ClientSession] = None
        self._tools_cache: List = []

    async def start_server(self):
        """Start FastMCP server as subprocess"""
        server_path = Path(__file__).parent / "server.py"
        self.server_process = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"MCP server started (PID: {self.server_process.pid})")

    async def connect(self):
        """Connect using stdio transport"""
        if self.session:
            return self.session
            
        if not self.server_process:
            await self.start_server()
            await asyncio.sleep(1)  # Let server initialize
            
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(Path(__file__).parent / "server.py")]
        )
        
        self.session = await stdio_client(server_params)
        await self.session.initialize()
        logger.info("Connected to MCP server")
        return self.session

    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools"""
        if self._tools_cache:
            return self._tools_cache
            
        session = await self.connect()
        tools_response = await session.list_tools()
        
        self._tools_cache = [
            {
                "name": tool.name,
                "description": tool.description or f"Tool: {tool.name}"
            }
            for tool in tools_response.tools
        ]
        return self._tools_cache

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool and return string result"""
        session = await self.connect()
        result = await session.call_tool(tool_name, arguments)
        
        # Extract text from MCP result
        if hasattr(result, 'content') and result.content:
            if isinstance(result.content, list) and result.content:
                return result.content[0].text
        return str(result)

    async def health_check(self) -> bool:
        """Check server health"""
        try:
            tools = await self.get_tools()
            return len(tools) > 0
        except:
            return False

    async def close(self):
        """Clean up resources"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
        self._tools_cache.clear()

# Global instance
_client = None

async def get_mcp_client() -> PDFMCPClient:
    global _client
    if _client is None:
        _client = PDFMCPClient()
    return _client
