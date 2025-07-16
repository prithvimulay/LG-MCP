from fastmcp import FastMCP
from pdf_mcp.tools.retrieval import retrieve_from_pdf
from pdf_mcp.tools.podcast import generate_podcast
from pdf_mcp.tools.selection import select_relevant_pdf
from pdf_mcp.pdf.manager import PDFManager
from pdf_mcp.vector.store import VectorStore

def register_tools(server: FastMCP):
    """Register all tools with the MCP server"""

    @server.tool(name="retrieve_from_pdf")
    def retrieve_from_pdf_tool(query: str, pdf_filename: str) -> str:
        """Retrieves specific information from a PDF document based on semantic search."""
        try:
            result = retrieve_from_pdf(query, pdf_filename)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    @server.tool(name="generate_podcast")
    def generate_podcast_tool(query: str, pdf_filename: str) -> str:
        """Generates a podcast-style dialogue based on PDF content."""
        try:
            result = generate_podcast(query, pdf_filename)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    @server.tool(name="select_relevant_pdf")
    def select_relevant_pdf_tool(query: str) -> str:
        """Identifies the most relevant PDF document based on the query."""
        try:
            result = select_relevant_pdf(query)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    @server.tool(name="list_pdfs")
    def list_pdfs_tool() -> str:
        """Lists all available PDF documents in the system."""
        try:
            manager = PDFManager()
            pdfs = manager.list_pdfs()
            if not pdfs:
                return "No PDFs found."
            return "\n".join(f"- {pdf.name}" for pdf in pdfs)
        except Exception as e:
            return f"Error: {str(e)}"

    @server.tool(name="db_status")
    def db_status_tool() -> str:
        """Provides detailed status of the vector database indexing."""
        try:
            vector_store = VectorStore()
            count = vector_store.collection.count()
            
            if count == 0:
                return "Vector database is empty. No PDFs have been indexed yet."
                
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
                
            return status
        except Exception as e:
            return f"Error: {str(e)}"