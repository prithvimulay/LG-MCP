# PDF MCP Server

A LangGraph + MCP adapter-based system for querying local PDFs and generating podcast scripts. This proof-of-concept system runs entirely over CLI using stdio-based MCP server and LangGraph agent integration.

## Features

- **PDF Document Processing**: Extract text, create chunks, and process PDFs from `data/pdfs/`
- **Vector-based Similarity Search**: ChromaDB for embeddings and similarity search
- **Question Answering**: Query PDF content using natural language
- **Podcast Generation**: Generate interview-style or educational podcast scripts from PDF content
- **Agent-based Routing**: LangGraph agent automatically selects the right tool based on user queries

# Ask questions about PDFs
uv run python -m pdf_mcp.langgraph.graph_runner "What is this PDF about?"

# Generate podcast scripts
uv run python -m pdf_mcp.langgraph.graph_runner "Generate a podcast about this PDF"

# List available PDFs
uv run python -m pdf_mcp.langgraph.graph_runner "List all PDFs"

# Select relevant PDF
uv run python -m pdf_mcp.langgraph.graph_runner "Select PDF about artificial intelligence"
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
                 


# terminal 1
uv run python -m pdf_mcp.mcp.server
# terminal 2
python lg_server_client.py http://localhost:5001/mcp/ 
# terminal 3
npx @modelcontextprotocol/inspector uv run python -m pdf_mcp.mcp.server


netstat -ano | findstr :5001
taskkill /PID 22380 /F


# 1. Retrieve information from PDF
tool:retrieve_from_pdf_tool "What is agentic AI?" "agenticAI.pdf"

# 2. List PDFs
tool:list_pdfs_tool

# 3. Check database status
tool:db_status_tool

# 4. Select relevant PDF
tool:select_relevant_pdf_tool "artificial intelligence agents"

# 5. Generate podcast
tool:generate_podcast_tool "AI concepts" "agenticAI.pdf"