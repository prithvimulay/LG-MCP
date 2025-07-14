import pypdf
from pathlib import Path
from typing import List, Union
from ..config.settings import settings

class PDFProcessor:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        from pdf_mcp.vector.store import VectorStore
        self.vector_store = VectorStore()

    def extract_text(self, pdf_path: Union[str, Path]) -> str:
        """Extract text from PDF file"""
        pdf_path = Path(pdf_path)
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def create_chunks(self, text: str) -> List[str]:
        """Split text into chunks"""
        chunks = []
        text_length = len(text)
        
        for i in range(0, text_length, self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
        
        return chunks

    def get_pdf_info(self, pdf_path: Union[str, Path]) -> dict:
        """Get basic PDF information"""
        pdf_path = Path(pdf_path)
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            return {
                "page_count": len(pdf_reader.pages),
                "file_size": pdf_path.stat().st_size
            }
            
    def index_pdf(self, pdf_path: Union[str, Path]) -> dict:
        """Extract text from PDF, create chunks, and store in vector DB
        Returns information about the indexing process
        """
        pdf_path = Path(pdf_path)
        try:
            # Extract text
            text = self.extract_text(pdf_path)
            if not text.strip():
                return {"success": False, "message": f"PDF contains no extractable text: {pdf_path.name}"}
                
            # Create chunks
            chunks = self.create_chunks(text)
            if not chunks:
                return {"success": False, "message": f"Could not create chunks from PDF: {pdf_path.name}"}
                
            # Store in vector DB with document metadata
            self.vector_store.add_chunks(chunks, pdf_path.name)
            
            return {
                "success": True, 
                "message": f"Successfully indexed PDF: {pdf_path.name}",
                "chunks": len(chunks),
                "characters": len(text)
            }
        except Exception as e:
            return {"success": False, "message": f"Error indexing PDF: {str(e)}"}
