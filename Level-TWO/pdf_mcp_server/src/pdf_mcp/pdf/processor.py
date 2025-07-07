import PyPDF2 as pypdf
from pathlib import Path
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config.settings import settings

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def chunk_text(self, text: str, pdf_id: str) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        chunks = self.text_splitter.split_text(text)

        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_docs.append({
                "content": chunk,
                "metadata": {
                    "pdf_id": pdf_id,
                    "chunk_index": i,
                    "source": pdf_id
                }
            })
        return chunk_docs

    def get_pdf_info(self, pdf_path: Path) -> Dict[str, Any]:
        """Get basic PDF information"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            return {
                "page_count": len(pdf_reader.pages),
                "file_size": pdf_path.stat().st_size
            }
