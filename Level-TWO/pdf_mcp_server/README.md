# PDF MCP Server

A LangGraph + MCP adapter-based system for querying local PDFs and generating podcast scripts. This proof-of-concept system runs entirely over CLI using stdio-based MCP server and LangGraph agent integration.

## Features

- **PDF Document Processing**: Extract text, create chunks, and process PDFs from `data/pdfs/`
- **Vector-based Similarity Search**: ChromaDB for embeddings and similarity search
- **Question Answering**: Query PDF content using natural language
- **Podcast Generation**: Generate interview-style or educational podcast scripts from PDF content
- **Agent-based Routing**: LangGraph agent automatically selects the right tool based on user queries

# Ask questions about PDFs
uv run python src/pdf_mcp/run_graph.py "What is this PDF about?"

# Generate podcast scripts
uv run python src/pdf_mcp/run_graph.py "Generate a podcast about this PDF"

# List available PDFs
uv run python src/pdf_mcp/run_graph.py "List all PDFs"

# Select relevant PDF
uv run python src/pdf_mcp/run_graph.py "Select PDF about artificial intelligence"
```

```
PDF_STORAGE_PATH=./data/pdfs
VECTOR_DB_PATH=./vector_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Development


## Example Output

```
🔍 Processing query: What is this PDF about?
📚 Found 1 PDF(s):
  - agenticAI.pdf

📝 Result:
🎯 **Query Results** (from agenticAI.pdf):

**1.**
The role of agentic AI in shaping a smart future: A systematic review...
```


pdf_mcp_server > uv init
pdf_mcp_server > uv venv
pdf_mcp_server > .venv\Scripts\activate
pdf_mcp_server > uv add -r requirements.txt
                 uv sync
                 uv run python -m pdf_mcp.tools_server
# terminal 1
npx @modelcontextprotocol/inspector --server http://localhost:5001    
# terminal 2
npx @modelcontextprotocol/inspector uv run python -m pdf_mcp.mcp.server