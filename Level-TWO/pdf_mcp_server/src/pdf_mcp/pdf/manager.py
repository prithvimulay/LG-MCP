from pathlib import Path
from typing import List
from typing import Dict, Any
from ..models.pdf import PDFDocument
from ..config.mongo import MongoManager
from ..config.settings import settings
from .processor import PDFProcessor
from ..vector.store import VectorStore

class PDFManager:
    def __init__(self):
        self.mongo = MongoManager()
        self.processor = PDFProcessor()
        self.vector_store = VectorStore()

        # Ensure directories exist
        settings.pdf_storage_path.mkdir(parents=True, exist_ok=True)
        settings.temp_storage_path.mkdir(parents=True, exist_ok=True)

    def scan_and_process_pdfs(self) -> List[str]:
        """Scan PDF directory and process new files"""
        pdf_files = list(settings.pdf_storage_path.glob("*.pdf"))
        existing_pdfs = {pdf.filename: pdf for pdf in self.mongo.get_all_pdfs()}

        processed_files = []

        for pdf_file in pdf_files:
            if pdf_file.name not in existing_pdfs:
                try:
                    # Get PDF info
                    pdf_info = self.processor.get_pdf_info(pdf_file)

                    # Create PDF document
                    pdf_doc = PDFDocument(
                        filename=pdf_file.name,
                        file_path=str(pdf_file),
                        file_size=pdf_info["file_size"],
                        page_count=pdf_info["page_count"],
                        processing_status="processing"
                    )

                    # Save to MongoDB
                    self.mongo.save_pdf(pdf_doc)

                    # Extract and chunk text
                    text = self.processor.extract_text(pdf_file)
                    chunks = self.processor.chunk_text(text, pdf_doc.id)

                    # Store in vector database
                    self.vector_store.add_chunks(chunks)

                    # Update status
                    pdf_doc.chunk_count = len(chunks)
                    pdf_doc.processing_status = "completed"
                    self.mongo.save_pdf(pdf_doc)

                    processed_files.append(pdf_file.name)

                except Exception as e:
                    import sys
                    print(f"Error processing {pdf_file.name}: {e}", file=sys.stderr)
                    # Update status to failed
                    if 'pdf_doc' in locals():
                        pdf_doc.processing_status = "failed"
                        self.mongo.save_pdf(pdf_doc)
                    raise e  # Re-raise to bubble up to the tool

        return processed_files

    def select_pdfs(self, pdf_identifiers: List[str]) -> List[str]:
        """Select PDFs by filename or index"""
        all_pdfs = self.mongo.get_all_pdfs()
        selected_names = []

        for identifier in pdf_identifiers:
            # Try by index first
            if identifier.isdigit():
                idx = int(identifier) - 1
                if 0 <= idx < len(all_pdfs):
                    pdf = all_pdfs[idx]
                    self.mongo.update_pdf_selection(pdf.id, True)
                    selected_names.append(pdf.filename)
            else:
                # Try by filename
                for pdf in all_pdfs:
                    if pdf.filename == identifier:
                        self.mongo.update_pdf_selection(pdf.id, True)
                        selected_names.append(pdf.filename)
                        break

        return selected_names

    def deselect_pdfs(self, pdf_identifiers: List[str]) -> List[str]:
        """Deselect PDFs by filename or index"""
        all_pdfs = self.mongo.get_all_pdfs()
        deselected_names = []

        for identifier in pdf_identifiers:
            if identifier.isdigit():
                idx = int(identifier) - 1
                if 0 <= idx < len(all_pdfs):
                    pdf = all_pdfs[idx]
                    self.mongo.update_pdf_selection(pdf.id, False)
                    deselected_names.append(pdf.filename)
            else:
                for pdf in all_pdfs:
                    if pdf.filename == identifier:
                        self.mongo.update_pdf_selection(pdf.id, False)
                        deselected_names.append(pdf.filename)
                        break

        return deselected_names

    def query_selected_pdfs(self, question: str) -> Dict[str, Any]:
        """Query selected PDFs"""
        selected_pdfs = self.mongo.get_selected_pdfs()

        if not selected_pdfs:
            return {
                "success": False,
                "message": "No PDFs are currently selected. Please select PDFs first.",
                "results": []
            }

        # Get PDF IDs
        pdf_ids = [pdf.id for pdf in selected_pdfs]

        # Search vector store
        results = self.vector_store.search(question, pdf_ids, settings.max_results)

        return {
            "success": True,
            "message": f"Found {len(results)} relevant chunks from {len(selected_pdfs)} selected PDFs",
            "results": results,
            "sources": [pdf.filename for pdf in selected_pdfs]
        }
