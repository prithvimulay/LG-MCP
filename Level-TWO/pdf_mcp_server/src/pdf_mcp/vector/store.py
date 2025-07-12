import chromadb
from chromadb.api.types import Documents, Embeddings
from typing import List
from sentence_transformers import SentenceTransformer
from ..config.settings import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(settings.vector_db_path))
        self.collection = self.client.get_or_create_collection("pdf_chunks")
        self.embedding_model = SentenceTransformer(settings.embedding_model)

    def add_chunks(self, chunks: List[str]):
        """Add text chunks to vector store"""
        embeddings = self.embedding_model.encode(chunks)
        doc_ids = [f"chunk_{i}" for i in range(len(chunks))]

        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=doc_ids
        )

    def similarity_search(self, query: str, texts: List[str], k: int = 5) -> List[str]:
        """Find the top-k most similar text chunks to a query."""
        query_embedding = self.embedding_model.encode([query])

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )

        # Return the most relevant chunks
        return results['documents'][0]
