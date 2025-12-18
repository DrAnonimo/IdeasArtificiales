"""
RAG system for CloudBees documentation.
Handles embedding generation, vector storage, and retrieval.
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import logging
import os
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG system for querying CloudBees documentation."""
    
    def __init__(self, 
                 collection_name: str = "cloudbees_kb",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 persist_directory: str = "./chroma_db"):
        """
        Initialize RAG system.
        
        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: Sentence transformer model name
            persist_directory: Directory to persist ChromaDB data
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"RAG system initialized. Collection: {collection_name}")
    
    def add_documents(self, chunks: List[Dict], batch_size: int = 4000):
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of chunks with 'text' and 'metadata'
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        total = len(chunks)
        logger.info(f"Adding {total} chunks to vector store in batches (batch_size={batch_size})...")

        # Process in batches to avoid ChromaDB max batch size error
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batch = chunks[start:end]

            texts = [chunk['text'] for chunk in batch]
            metadatas = [chunk.get('metadata', {}) for chunk in batch]
            # Use UUIDs to avoid ID collisions between runs
            ids = [str(uuid.uuid4()) for _ in range(len(batch))]

            # Generate embeddings for this batch
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added batch {start}-{end} ({end - start} chunks)")

        logger.info(f"Successfully added {total} chunks")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant chunks with 'text', 'metadata', and 'distance'
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                    'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else None
                })
        
        return formatted_results
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection."""
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'document_count': count
        }
    
    def list_documents(self, limit: Optional[int] = None) -> List[Dict]:
        """
        List all documents in the collection with their metadata.
        
        Args:
            limit: Maximum number of documents to return (None for all)
            
        Returns:
            List of documents with metadata
        """
        count = self.collection.count()
        if count == 0:
            return []
        
        # Get all documents from ChromaDB
        n_results = limit if limit else count
        results = self.collection.get(limit=n_results)
        
        # Group by URL to show unique documents
        documents_by_url = {}
        if results['ids']:
            for i, doc_id in enumerate(results['ids']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                url = metadata.get('url', 'Unknown')
                title = metadata.get('title', 'Untitled')
                
                if url not in documents_by_url:
                    documents_by_url[url] = {
                        'url': url,
                        'title': title,
                        'chunk_count': 0
                    }
                documents_by_url[url]['chunk_count'] += 1
        
        return list(documents_by_url.values())

