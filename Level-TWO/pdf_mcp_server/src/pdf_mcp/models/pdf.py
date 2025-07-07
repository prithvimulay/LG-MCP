from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

class PDFDocument(BaseModel):
    id: Optional[str] = None
    filename: str
    file_path: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_size: int
    page_count: int = 0
    chunk_count: int = 0
    is_selected: bool = False
    processing_status: str = "pending"  # pending, processing, completed, failed

class PDFCollection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "default"
    pdf_documents: List[str] = Field(default_factory=list)  # PDF IDs
    selected_pdfs: List[str] = Field(default_factory=list)  # Selected PDF IDs
    created_date: datetime = Field(default_factory=datetime.utcnow)
