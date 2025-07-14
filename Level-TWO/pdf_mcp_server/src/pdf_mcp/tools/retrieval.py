from pdf_mcp.pdf.manager import PDFManager
from pdf_mcp.pdf.processor import PDFProcessor
from pdf_mcp.vector.store import VectorStore
from pathlib import Path
from pdf_mcp.config.settings import settings

pdf_manager = PDFManager()
pdf_processor = PDFProcessor()
vector_store = VectorStore()

def retrieve_from_pdf(query: str, pdf_path: str) -> str:
    # Handle file path vs filename
    if pdf_path.startswith(str(settings.pdf_storage_path)):
        # Full path provided
        full_path = Path(pdf_path)
        pdf_filename = full_path.name
    else:
        # Filename provided
        pdf_filename = Path(pdf_path).name
        full_path = settings.pdf_storage_path / pdf_filename

    # Validate PDF exists
    if not pdf_manager.validate_pdf(full_path):
        return f"Invalid PDF path: {pdf_path}. File not found at {full_path}"
    
    # Ensure the PDF is indexed in the vector database
    collection_count = vector_store.collection.count()
    if collection_count == 0:
        # Index the PDF if the collection is empty
        index_result = pdf_processor.index_pdf(full_path)
        if not index_result["success"]:
            return f"Failed to index PDF: {index_result['message']}"
    
    # Search for relevant chunks in the vector database
    relevant = vector_store.similarity_search(query, pdf_filename=pdf_filename, k=3)

    if not relevant or len(relevant) == 0:
        # If nothing found, try to reindex and search again
        index_result = pdf_processor.index_pdf(full_path)
        if not index_result["success"]:
            return f"Failed to index PDF: {index_result['message']}"
            
        # Try search again after reindexing
        relevant = vector_store.similarity_search(query, pdf_filename=pdf_filename, k=3)
        if not relevant or len(relevant) == 0:
            return f"No relevant results found for query '{query}' in PDF '{pdf_filename}'."

    # Format the results
    return "\n\n".join([f"Result {i+1}:\n{chunk[:300]}..." if len(chunk) > 300 else f"Result {i+1}:\n{chunk}" for i, chunk in enumerate(relevant)])
