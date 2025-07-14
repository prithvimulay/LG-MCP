from mcp.types import Resource
from pathlib import Path
from pdf_mcp.pdf.processor import PDFProcessor
from pdf_mcp.pdf.manager import PDFManager

def register_resources(server):
    pdf_manager = PDFManager()
    pdf_processor = PDFProcessor()

    @server.resource_provider
    def list_resources():
        """Expose all local PDFs as MCP resources."""
        pdfs = pdf_manager.list_pdfs()
        return [
            Resource(
                uri=f"resource://{pdf.name}",
                name=pdf.name,
                description=f"PDF file stored at {pdf}",
                metadata={
                    "file_size": pdf.stat().st_size,
                    "path": str(pdf)
                }
            )
            for pdf in pdfs
        ]

    @server.resource_reader
    def get_resource_content(uri: str) -> str:
        """Return text extracted from a PDF resource."""
        if not uri.startswith("resource://"):
            raise ValueError("Invalid resource URI format.")

        filename = uri.replace("resource://", "")
        file_path = Path("data/pdfs") / filename

        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        return pdf_processor.extract_text(file_path)
