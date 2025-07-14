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

    def add_chunks(self, chunks: List[str], pdf_filename: str = None):
        """Add text chunks to vector store with PDF source metadata"""
        # Generate embeddings for all chunks
        embeddings = self.embedding_model.encode(chunks)
        
        # Create unique IDs for each chunk
        import uuid
        doc_ids = [f"{pdf_filename}_{uuid.uuid4()}" for _ in range(len(chunks))]
        
        # Create metadata for each chunk to track source PDF
        metadatas = [{"source": pdf_filename} for _ in range(len(chunks))] if pdf_filename else None
        
        # Add to collection
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=doc_ids,
            metadatas=metadatas
        )

    def similarity_search(self, query: str, pdf_filename: str = None, k: int = 5) -> List[str]:
        """Find the top-k most similar text chunks to a query from the vector database.
        
        Args:
            query: The query text to find similar chunks for
            pdf_filename: Optional filename to filter results to a specific PDF
            k: Number of results to return
            
        Returns:
            List of text chunks most similar to the query
        """
        # Encode the query
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Set up search parameters
        where_filter = None
        if pdf_filename:
            where_filter = {"source": pdf_filename}
            
        # Perform search against vector DB
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_filter
            )
            
            # Extract documents from results
            if results and 'documents' in results and len(results['documents']) > 0:
                chunks = results['documents'][0]
                if not chunks:
                    return []
                return chunks
            return []
            
        except Exception as e:
            import logging
            logging.error(f"Error in similarity search: {str(e)}")
            return []
