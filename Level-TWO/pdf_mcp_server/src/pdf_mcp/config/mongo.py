from pymongo import MongoClient
from typing import List, Optional, Dict, Any
from ..models.pdf import PDFDocument, PDFCollection
from .settings import settings

class MongoManager:
    def __init__(self):
        self.client = MongoClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_database]
        self.pdfs = self.db.pdfs
        self.collections = self.db.collections

    def save_pdf(self, pdf: PDFDocument) -> str:
        pdf_data = pdf.model_dump()
        
        if pdf.id and pdf.id != "":
            # Update existing document
            from bson import ObjectId
            result = self.pdfs.replace_one(
                {"_id": ObjectId(pdf.id)},
                pdf_data
            )
            return pdf.id
        else:
            # Create new document
            result = self.pdfs.insert_one(pdf_data)
            # Update the PDF object with the MongoDB _id
            pdf.id = str(result.inserted_id)
            return str(result.inserted_id)

    def get_all_pdfs(self) -> List[PDFDocument]:
        docs = list(self.pdfs.find({}))
        # Convert MongoDB _id to id field
        for doc in docs:
            if '_id' in doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
        return [PDFDocument(**doc) for doc in docs]

    def update_pdf_selection(self, pdf_id: str, is_selected: bool):
        from bson import ObjectId
        self.pdfs.update_one(
            {"_id": ObjectId(pdf_id)},
            {"$set": {"is_selected": is_selected}}
        )

    def get_selected_pdfs(self) -> List[PDFDocument]:
        docs = list(self.pdfs.find({"is_selected": True}))
        # Convert MongoDB _id to id field
        for doc in docs:
            if '_id' in doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
        return [PDFDocument(**doc) for doc in docs]

    def clear_all_selections(self):
        self.pdfs.update_many({}, {"$set": {"is_selected": False}})
