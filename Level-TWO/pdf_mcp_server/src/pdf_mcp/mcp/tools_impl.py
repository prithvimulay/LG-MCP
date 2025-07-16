from fastmcp import FastMCP
import mcp.types as types
from pdf_mcp.tools.retrieval import retrieve_from_pdf
from pdf_mcp.tools.podcast import generate_podcast
from pdf_mcp.tools.selection import select_relevant_pdf
from pdf_mcp.pdf.manager import PDFManager

def list_pdfs() -> str:
    manager = PDFManager()
    pdfs = manager.list_pdfs()
    if not pdfs:
        return "No PDFs found."
    return "\n".join(f"- {pdf.name}" for pdf in pdfs)

# Define available tools using types.Tool
TOOLS = [
    types.Tool(
        name="retrieve_from_pdf",
        description="Retrieves specific information from a PDF document based on semantic search.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The specific question or search query to find information in the PDF."},
                "pdf_filename": {"type": "string", "description": "The exact filename of the PDF to search within (e.g., 'document.pdf')."},
            },
            "required": ["query", "pdf_filename"]
        }
    ),
    types.Tool(
        name="generate_podcast",
        description="Generates a podcast-style dialogue based on PDF content.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The topic or theme for the podcast generation."},
                "pdf_filename": {"type": "string", "description": "The exact filename of the PDF to use as source material."},
            },
            "required": ["query", "pdf_filename"]
        }
    ),
    types.Tool(
        name="select_relevant_pdf",
        description="Identifies the most relevant PDF document based on the query.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search term or topic to match against available PDF filenames."},
            },
            "required": ["query"]
        }
    ),
    types.Tool(
        name="list_pdfs",
        description="Lists all available PDF documents in the system.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    types.Tool(
        name="db_status",
        description="Provides detailed status of the vector database indexing.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
]

def register_tools(server: FastMCP):
    """Register all tools with the MCP server"""
    
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """Return the list of available tools"""
        return TOOLS
    
    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution based on tool name"""
        try:
            if name == "retrieve_from_pdf":
                query = arguments["query"]
                pdf_filename = arguments["pdf_filename"]
                result = retrieve_from_pdf(query, pdf_filename)
                return [types.TextContent(type="text", text=result)]
                
            elif name == "generate_podcast":
                query = arguments["query"]
                pdf_filename = arguments["pdf_filename"]
                result = generate_podcast(query, pdf_filename)
                return [types.TextContent(type="text", text=result)]
                
            elif name == "select_relevant_pdf":
                query = arguments["query"]
                result = select_relevant_pdf(query)
                return [types.TextContent(type="text", text=result)]
                
            elif name == "list_pdfs":
                result = list_pdfs()
                return [types.TextContent(type="text", text=result)]
                
            elif name == "db_status":
                from pdf_mcp.vector.store import VectorStore
                vector_store = VectorStore()
                count = vector_store.collection.count()
                
                if count == 0:
                    result = "Vector database is empty. No PDFs have been indexed yet."
                    return [types.TextContent(type="text", text=result)]
                    
                # Get all items to analyze
                items = vector_store.collection.get()
                
                # Count documents by source PDF
                pdf_counts = {}
                if items and 'metadatas' in items and items['metadatas']:
                    for metadata in items['metadatas']:
                        if metadata and 'source' in metadata:
                            source = metadata['source']
                            pdf_counts[source] = pdf_counts.get(source, 0) + 1
                
                # Build status message
                status = f"Vector database contains {count} total chunks.\n\n"
                status += "Indexed PDFs:\n"
                
                for pdf, chunk_count in pdf_counts.items():
                    status += f"- {pdf}: {chunk_count} chunks\n"
                    
                return [types.TextContent(type="text", text=status)]
                
            # Handle error case for unknown tool
            return [types.TextContent(
                type="text", 
                text=f"Error: Tool '{name}' not found"
            )]
            
        except Exception as error:
            # Proper error handling according to MCP
            return [types.TextContent(
                type="text", 
                text=f"Error: {str(error)}"
            )]
