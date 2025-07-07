import chromadb
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from ..config.settings import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(settings.chroma_db_path))
        self.collection = self.client.get_or_create_collection("pdf_chunks")
        self.embeddings = SentenceTransformer(settings.embedding_model)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Add text chunks to vector store"""
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [f"{chunk['metadata']['pdf_id']}_chunk_{chunk['metadata']['chunk_index']}"
               for chunk in chunks]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, pdf_ids: List[str], max_results: int = 5) -> List[Dict]:
        """Search for relevant chunks in selected PDFs"""
        # Create filter for selected PDFs
        where_filter = {"pdf_id": {"$in": pdf_ids}} if pdf_ids else {}

        results = self.collection.query(
            query_texts=[query],
            n_results=max_results,
            where=where_filter
        )

        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None
                })

        return formatted_results

    def delete_pdf_chunks(self, pdf_id: str):
        """Delete all chunks for a specific PDF"""
        # Get all chunk IDs for this PDF
        results = self.collection.get(where={"pdf_id": pdf_id})
        if results['ids']:
            self.collection.delete(ids=results['ids'])
