pdf_mcp_server > uv init
pdf_mcp_server > uv venv
pdf_mcp_server > .venv\Scripts\activate
pdf_mcp_server > uv add -r requirements.txt
uv sync
uv run python -m src.pdf_mcp.server 