from fastmcp.tools import tool
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

def register_tools(server):
    @server.tool
    def retrieve_from_pdf_tool(query: str, pdf_filename: str) -> str:
        return retrieve_from_pdf(query, pdf_filename)
    
    @server.tool
    def generate_podcast_tool(query: str, pdf_filename: str) -> str:
        return generate_podcast(query, pdf_filename)
    
    @server.tool
    def select_relevant_pdf_tool(query: str) -> str:
        return select_relevant_pdf(query)
    
    @server.tool
    def list_pdfs_tool() -> str:
        return list_pdfs()
        
    @server.tool
    def db_status_tool() -> str:
        """Show the current status of the vector database"""
        from pdf_mcp.vector.store import VectorStore
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
