from pdf_mcp.pdf.manager import PDFManager
from pdf_mcp.pdf.processor import PDFProcessor
from pdf_mcp.vector.store import VectorStore
from pathlib import Path

pdf_manager = PDFManager()
pdf_processor = PDFProcessor()
vector_store = VectorStore()

def retrieve_from_pdf(query: str, pdf_path: str) -> str:
    if not pdf_manager.validate_pdf(Path(pdf_path)):
        return f"Invalid PDF path: {pdf_path}"
    
    text = pdf_processor.extract_text(pdf_path)
    chunks = pdf_processor.create_chunks(text)
    relevant = vector_store.similarity_search(query, chunks, k=3)

    if not relevant:
        return "No relevant results found."

    return "\n".join([f"{i+1}. {chunk}" for i, chunk in enumerate(relevant)])
