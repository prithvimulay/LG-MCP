#!/usr/bin/env python3
"""
PDF MCP Server - MVP Implementation
"""

import sys
from mcp.server.fastmcp import FastMCP
from .tools.pdf_tools import register_tools
from .tools.podcast_tools import register_podcast_tools
from .config.settings import settings

# Initialize FastMCP server
mcp = FastMCP("pdf-mcp-server")

# Register all PDF tools
register_tools(mcp)

# Register podcast tools
register_podcast_tools(mcp)

if __name__ == "__main__":
    print(f"Starting PDF MCP Server...", file=sys.stderr)
    print(f"PDF Storage: {settings.pdf_storage_path}", file=sys.stderr)
    print(f"MongoDB: {settings.mongodb_url}", file=sys.stderr)
    print(f"Vector DB: {settings.chroma_db_path}", file=sys.stderr)

    # Run the server
    mcp.run(transport='stdio')
