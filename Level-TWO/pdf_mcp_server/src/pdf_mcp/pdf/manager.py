from pathlib import Path
from typing import List
from ..config.settings import settings

class PDFManager:
    def __init__(self):
        settings.pdf_storage_path.mkdir(parents=True, exist_ok=True)
    
    def list_pdfs(self) -> List[Path]:
        """List all PDF files in the storage directory"""
        return list(settings.pdf_storage_path.glob("*.pdf"))
    
    def validate_pdf(self, pdf_path: Path) -> bool:
        """Validate that a PDF file exists and is readable"""
        return pdf_path.exists() and pdf_path.is_file() and pdf_path.suffix.lower() == '.pdf'
    
    def get_pdf_info(self, pdf_path: Path) -> dict:
        """Get basic information about a PDF file"""
        if not self.validate_pdf(pdf_path):
            raise ValueError(f"Invalid PDF file: {pdf_path}")
        
        return {
            "filename": pdf_path.name,
            "file_path": str(pdf_path),
            "file_size": pdf_path.stat().st_size,
            "exists": True
        }
