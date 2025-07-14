from fastmcp import FastMCP
from pdf_mcp.mcp.tools_impl import register_tools
from pdf_mcp.mcp.prompts_impl import register_prompts
# from pdf_mcp.mcp.resources_impl import register_resources  # can re-enable later

server = FastMCP(name="pdf-mcp-server", version="1.0.0")

register_tools(server)
register_prompts(server)
# register_resources(server)

if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=5001)


