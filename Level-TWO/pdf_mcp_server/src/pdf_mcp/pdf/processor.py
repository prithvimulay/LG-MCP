import pypdf
from pathlib import Path
from typing import List, Union
from ..config.settings import settings

class PDFProcessor:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

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
