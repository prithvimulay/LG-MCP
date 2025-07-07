pdf_mcp_server > uv init
pdf_mcp_server > uv venv
pdf_mcp_server > .venv\Scripts\activate
pdf_mcp_server > uv add -r requirements.txt
uv sync




uv run python -c "from src.pdf_mcp.config.mongo import MongoManager; mm = MongoManager(); mm.pdfs.drop(); print('Cleared PDF collection')"

uv run python -c "from src.pdf_mcp.vector.store import VectorStore; vs = VectorStore(); vs.client.delete_collection('pdf_chunks'); print('Cleared vector collection')"