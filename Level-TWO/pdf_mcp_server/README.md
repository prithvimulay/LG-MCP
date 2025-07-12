# PDF MCP Server

A LangGraph + MCP adapter-based system for querying local PDFs and generating podcast scripts. This proof-of-concept system runs entirely over CLI using stdio-based MCP server and LangGraph agent integration.

## Features

- **PDF Document Processing**: Extract text, create chunks, and process PDFs from `data/pdfs/`
- **Vector-based Similarity Search**: ChromaDB for embeddings and similarity search
- **Question Answering**: Query PDF content using natural language
- **Podcast Generation**: Generate interview-style or educational podcast scripts from PDF content
- **Agent-based Routing**: LangGraph agent automatically selects the right tool based on user queries

## Architecture

### Core Components

- **MCP Tools** (`tools_server.py`): Exposes 4 tools via `@tool` decorators:
  - `retrieve_from_pdf(query, pdf_path)`: Answer questions about PDF content
  - `generate_podcast(pdf_path)`: Generate podcast scripts from PDF
  - `select_relevant_pdf(query)`: Select most relevant PDF for a query
  - `list_pdfs()`: List all available PDF files

- **LangGraph Agent** (`run_graph.py`): CLI entrypoint that:
  - Loads the ConversationState model
  - Routes queries to appropriate tools
  - Returns formatted responses

- **Helper Modules**:
  - `pdf/`: PDF processing and management
  - `vector/`: ChromaDB embedding and similarity search
  - `podcast/`: Podcast script generation with templates

## Installation

1. Install dependencies using uv:
```bash
uv sync
```

2. Set up environment variables in `.env` (already configured)

3. Place PDF files in `data/pdfs/` directory

## Usage

### Basic Queries

```bash
# Ask questions about PDFs
uv run python src/pdf_mcp/run_graph.py "What is this PDF about?"

# Generate podcast scripts
uv run python src/pdf_mcp/run_graph.py "Generate a podcast about this PDF"

# List available PDFs
uv run python src/pdf_mcp/run_graph.py "List all PDFs"

# Select relevant PDF
uv run python src/pdf_mcp/run_graph.py "Select PDF about artificial intelligence"
```

### Interactive Mode

```bash
uv run python src/pdf_mcp/run_graph.py
# Will prompt for input
```

## Project Structure

```
pdf-mcp-server/
├── data/
│   └── pdfs/                     # User-uploaded PDF documents
├── vector_db/                    # ChromaDB vector index storage
├── src/
│   └── pdf_mcp/
│       ├── tools_server.py       # MCP tool server with @tool functions
│       ├── run_graph.py          # LangGraph + MCP adapter entrypoint
│       ├── config/
│       │   └── settings.py       # Global project settings
│       ├── models/
│       │   └── session.py        # ConversationState Pydantic model
│       ├── pdf/
│       │   ├── manager.py        # PDF listing, validation, file checks
│       │   └── processor.py      # PDF loading, chunking, text preprocessing
│       ├── podcast/
│       │   ├── processor.py      # Podcast script builder
│       │   └── prompts.py        # Prompt templates (speaker styles, tone)
│       ├── utils/
│       │   └── logger.py         # Logging setup and helpers
│       └── vector/
│           └── store.py          # ChromaDB embedding + similarity search
├── requirements.txt
├── .env
└── README.md
```

## Configuration

The system uses environment variables defined in `.env`:

```
PDF_STORAGE_PATH=./data/pdfs
VECTOR_DB_PATH=./vector_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Development

### Adding New Tools

1. Add new functions to `tools_server.py` with `@tool` decorator
2. Update the routing logic in `run_graph.py` if needed
3. Test with various query patterns

### ConversationState Model

The `ConversationState` Pydantic model handles the flow:

```python
class ConversationState(BaseModel):
    query: str
    pdf_path: Optional[str] = None
    response: Optional[str] = None
```

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
uv run python -m src.pdf_mcp.tools_server
