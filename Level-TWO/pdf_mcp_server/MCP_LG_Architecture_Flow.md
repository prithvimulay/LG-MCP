# MCP + LangGraph Architecture Flow

## How LangGraph Accesses MCP Server Tools

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER QUERY INPUT                                 │
│                          "List all PDFs"                                   │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLI INTERFACE                                        │
│               (pdf_mcp.cli.py - MCPWorkflowCLI)                           │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATOR                                  │
│                (LangGraphPDFOrchestrator)                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    INITIALIZATION PHASE                             │    │
│  │                                                                     │    │
│  │  1. await get_mcp_client()  ← Creates PDFMCPClient                 │    │
│  │  2. raw_tools = await self.mcp_client.get_tools()                  │    │
│  │  3. self.tools_list = list(raw_tools.values())                     │    │
│  │  4. llm_with_tools = self.llm.bind_tools(self.tools_list)          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MCP CLIENT                                          │
│                    (PDFMCPClient)                                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    TOOL DISCOVERY                                  │    │
│  │                                                                     │    │
│  │  self.client = MultiServerMCPClient({                              │    │
│  │      "pdf_mcp": {                                                   │    │
│  │          "command": "python",                                       │    │
│  │          "args": ["-m", "pdf_mcp.mcp.server"],                     │    │
│  │          "transport": "stdio"                                       │    │
│  │      }                                                              │    │
│  │  })                                                                 │    │
│  │                                                                     │    │
│  │  # Launches subprocess: python -m pdf_mcp.mcp.server               │    │
│  │  # Communicates via STDIO (JSON-RPC over pipes)                    │    │
│  │                                                                     │    │
│  │  self.tools = await self.client.get_tools()                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          │ STDIO Transport (JSON-RPC)
                          │ ┌─────────────────────────────┐
                          │ │ { "method": "tools/list" }  │
                          │ └─────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MCP SERVER                                          │
│                  (FastMCP via pdf_mcp.mcp.server)                         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    TOOL REGISTRATION                                │    │
│  │                                                                     │    │
│  │  @server.tool()                                                     │    │
│  │  def list_pdfs_tool() -> str:                                       │    │
│  │      # Implementation in tools_impl.py                              │    │
│  │                                                                     │    │
│  │  @server.tool()                                                     │    │
│  │  def retrieve_from_pdf_tool(query, pdf_filename) -> str:            │    │
│  │      # Implementation in tools_impl.py                              │    │
│  │                                                                     │    │
│  │  # More tools: db_status_tool, generate_podcast_tool, etc.         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Returns tool metadata via STDIO:                                          │
│  {                                                                          │
│    "tools": [                                                              │
│      {"name": "list_pdfs_tool", "description": "...", "parameters": {}},   │
│      {"name": "retrieve_from_pdf_tool", "description": "...", ...}         │
│    ]                                                                        │
│  }                                                                          │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          │ Tool metadata returned
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH EXECUTION                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      AGENT NODE                                     │    │
│  │                                                                     │    │
│  │  # LLM with bound tools analyzes user query                         │    │
│  │  response = await llm_with_tools.ainvoke(messages)                  │    │
│  │                                                                     │    │
│  │  # LLM decides: "This query needs list_pdfs_tool"                   │    │
│  │  # Creates tool_call: {"name": "list_pdfs_tool", "args": {}}        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MCP TOOL NODE                                    │    │
│  │                                                                     │    │
│  │  for tool_call in last_message.tool_calls:                         │    │
│  │      tool_name = tool_call["name"]  # "list_pdfs_tool"              │    │
│  │      tool_args = tool_call.get("args") or {}                        │    │
│  │                                                                     │    │
│  │      proxy = self.tools_map.get(tool_name)                          │    │
│  │      raw_result = await proxy.ainvoke(tool_args)                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          │ Tool execution request via MCP Client
                          │ ┌─────────────────────────────────────────────┐
                          │ │ { "method": "tools/call",                   │
                          │ │   "params": {                               │
                          │ │     "name": "list_pdfs_tool",               │
                          │ │     "arguments": {}                         │
                          │ │   }                                         │
                          │ │ }                                           │
                          │ └─────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MCP SERVER EXECUTION                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                TOOL FUNCTION EXECUTION                              │    │
│  │                                                                     │    │
│  │  def list_pdfs_tool() -> str:                                       │    │
│  │      manager = PDFManager()                                         │    │
│  │      pdfs = manager.list_pdfs()                                     │    │
│  │      # Process and format results                                   │    │
│  │      return formatted_result                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Returns result via STDIO:                                                 │
│  {                                                                          │
│    "result": "=== Available PDF Documents (3 total) ===\n1. file1.pdf..." │
│  }                                                                          │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          │ Result returned
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RESPONSE FORMATTING                                   │
│                                                                             │
│  LangGraph receives tool result and formats final response for user        │
│  │                                                                          │
│  ▼                                                                          │
│  final_message = result["messages"][-1]                                     │
│  return final_message.content                                              │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLI OUTPUT                                           │
│                                                                             │
│  AI Assistant (via MCP Workflow):                                          │
│  ──────────────────────────────────────────────────────────────────────────  │
│  === Available PDF Documents (3 total) ===                                 │
│                                                                             │
│     1. agenticAI.pdf                                                       │
│     2. attention.pdf                                                       │
│     3. roleAI.pdf                                                          │
│                                                                             │
│  === Available Operations ===                                              │
│  - Search content in any PDF                                               │
│  - Generate podcast from PDF content                                       │
│  - Check vector database status                                            │
│  ──────────────────────────────────────────────────────────────────────────  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Components Explained

### 1. **MCP Client Role (ESSENTIAL - Cannot be excluded)**

The MCP Client (`PDFMCPClient` using `MultiServerMCPClient`) serves as a **protocol bridge** between LangGraph and MCP servers. According to the MCP specification:

**Why MCP Client is Required:**
- **Protocol Translation**: MCP uses JSON-RPC over various transports (stdio, HTTP, WebSockets)
- **Tool Discovery**: Client discovers available tools from servers via `tools/list` RPC calls
- **Tool Execution**: Client sends `tools/call` RPC requests to execute tools
- **Connection Management**: Handles subprocess lifecycle, communication pipes, error recovery
- **Serialization**: Converts Python function calls to JSON-RPC and back

**From the code:**
```python
# In mcp_client.py
self.client = MultiServerMCPClient({
    "pdf_mcp": {
        "command": "python",                    # Launch server process
        "args": ["-m", "pdf_mcp.mcp.server"],  # Server module
        "transport": "stdio"                    # Communication method
    }
})
```

### 2. **MCP Server (FastMCP)**

The server runs as a separate process and:
- **Tool Registration**: Registers functions as MCP tools via decorators
- **RPC Handling**: Listens for JSON-RPC calls on stdio
- **Tool Execution**: Executes the actual tool functions
- **Result Serialization**: Returns results as JSON-RPC responses

### 3. **LangGraph Integration**

LangGraph doesn't directly communicate with MCP - it uses the adapter layer:
- **Tool Binding**: `llm.bind_tools(self.tools_list)` makes LLM aware of available tools
- **Tool Selection**: LLM analyzes queries and generates tool calls
- **Execution**: LangGraph routes tool calls through MCP client to server

## Can MCP Client be Excluded?

**NO - The MCP Client cannot be excluded** because:

1. **Protocol Requirement**: MCP defines a specific JSON-RPC protocol that must be followed
2. **Process Management**: Someone needs to launch and manage the MCP server subprocess
3. **Communication**: STDIO transport requires careful handling of pipes and serialization
4. **Tool Discovery**: No other mechanism exists to discover MCP server capabilities
5. **Adapter Function**: `langchain-mcp-adapters` specifically bridges LangChain/LangGraph with MCP

**Alternative Architectures (without MCP):**
If you wanted to avoid MCP entirely, you could:
- Direct function calls (lose inter-process isolation)
- REST API (more complex, lose stdio efficiency)
- Custom RPC protocol (reinvent MCP)

But then you wouldn't be using MCP at all - you'd be building a different architecture.

The MCP client is the **essential bridge** that makes the entire system work according to the Model Context Protocol specification.
