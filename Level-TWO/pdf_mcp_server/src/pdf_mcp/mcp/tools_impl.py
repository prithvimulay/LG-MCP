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
        """Retrieves specific information from a PDF document based on semantic search.
        
        Args:
            query: The specific question or search query to find information in the PDF.
            pdf_filename: The exact filename of the PDF to search within (e.g., 'document.pdf').
            
        Returns:
            The most relevant text excerpts from the PDF that answer the query.
            
        This tool performs vector-based semantic search on PDF content and returns the most relevant passages.
        It automatically indexes the PDF if needed before searching.
        """
        return retrieve_from_pdf(query, pdf_filename)
    
    @server.tool
    def generate_podcast_tool(query: str, pdf_filename: str) -> str:
        """Generates a podcast-style dialogue based on PDF content.
        
        Args:
            query: The topic or theme for the podcast generation.
            pdf_filename: The exact filename of the PDF to use as source material.
            
        Returns:
            A formatted podcast script with intro and dialogue based on PDF content.
            
        This tool creates conversational content from PDF text, formatting it as a dialogue
        between speakers discussing the specified topic.
        """
        return generate_podcast(query, pdf_filename)
    
    @server.tool
    def select_relevant_pdf_tool(query: str) -> str:
        """Identifies the most relevant PDF document based on the query.
        
        Args:
            query: The search term or topic to match against available PDF filenames.
            
        Returns:
            The filename of the most relevant PDF based on keyword matching.
            
        This tool analyzes the query and compares it with available PDF filenames to determine
        which document is most likely to contain relevant information. Use this when the user
        hasn't specified which PDF to use.
        """
        return select_relevant_pdf(query)
    
    @server.tool
    def list_pdfs_tool() -> str:
        """Lists all available PDF documents in the system.
        
        Returns:
            A formatted list of all PDF filenames available for processing.
            
        This tool retrieves and displays all PDF documents that are currently accessible
        in the system. Use this to check available documents before performing operations
        or when the user asks what documents are available.
        """
        return list_pdfs()
        
    @server.tool
    def db_status_tool() -> str:
        """Provides detailed status of the vector database indexing.
        
        Returns:
            A report showing the total number of indexed chunks and a breakdown by PDF.
            
        This tool checks the current state of the vector database, showing which PDFs
        have been indexed and how many chunks each contains. Use this to verify indexing
        status before performing searches or to diagnose search-related issues.
        """
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
