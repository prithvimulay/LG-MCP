from pathlib import Path
from pdf_mcp.pdf.processor import PDFProcessor
from pdf_mcp.pdf.manager import PDFManager
from pdf_mcp.config.settings import settings
import logging

def index_all_pdfs():
    """Index all PDFs in the storage directory at startup"""
    logging.info("Starting PDF indexing process...")
    
    processor = PDFProcessor()
    manager = PDFManager()
    
    pdfs = manager.list_pdfs()
    if not pdfs:
        logging.warning("No PDFs found in storage directory")
        return
    
    logging.info(f"Found {len(pdfs)} PDFs to index")
    
    indexed = 0
    failed = 0
    
    for pdf_path in pdfs:
        result = processor.index_pdf(pdf_path)
        if result["success"]:
            indexed += 1
            logging.info(f"Indexed PDF: {pdf_path.name} - {result['chunks']} chunks")
        else:
            failed += 1
            logging.error(f"Failed to index PDF: {pdf_path.name} - {result['message']}")
    
    logging.info(f"Indexing complete: {indexed} PDFs indexed, {failed} failed")
    
    return {"indexed": indexed, "failed": failed}

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run indexing
    result = index_all_pdfs()
    print(f"Indexing complete: {result}")
