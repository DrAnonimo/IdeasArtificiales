"""
Document chunking utilities for RAG.
Splits documents into smaller chunks suitable for embedding and retrieval.
"""
from typing import List, Dict
import re


class DocumentChunker:
    """Chunks documents into smaller pieces for RAG."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target size of chunks (in characters)
            chunk_overlap: Overlap between chunks (in characters)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with 'text' and 'metadata'
        """
        if not text:
            return []
        
        # Try to split on paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_length = len(para)
            
            # If paragraph is larger than chunk_size, split it further
            if para_length > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append({
                        'text': chunk_text,
                        'metadata': metadata or {}
                    })
                    current_chunk = []
                    current_length = 0
                
                # Split large paragraph by sentences
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    sent_length = len(sentence)
                    if current_length + sent_length > self.chunk_size and current_chunk:
                        chunk_text = '\n\n'.join(current_chunk)
                        chunks.append({
                            'text': chunk_text,
                            'metadata': metadata or {}
                        })
                        # Keep overlap
                        overlap_text = self._get_overlap_text(current_chunk)
                        current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                        current_length = len('\n\n'.join(current_chunk))
                    else:
                        current_chunk.append(sentence)
                        current_length += sent_length + 2  # +2 for '\n\n'
            
            # If adding this paragraph would exceed chunk_size
            elif current_length + para_length > self.chunk_size:
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append({
                        'text': chunk_text,
                        'metadata': metadata or {}
                    })
                    # Keep overlap
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = [overlap_text, para] if overlap_text else [para]
                    current_length = len('\n\n'.join(current_chunk))
                else:
                    current_chunk = [para]
                    current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length + 2  # +2 for '\n\n'
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'metadata': metadata or {}
            })
        
        return chunks
    
    def _get_overlap_text(self, chunks: List[str]) -> str:
        """Get overlap text from the end of chunks."""
        if not chunks:
            return ""
        
        # Take last chunk and get last part of it
        last_chunk = chunks[-1]
        if len(last_chunk) <= self.chunk_overlap:
            return last_chunk
        
        # Try to split at sentence boundary
        sentences = re.split(r'(?<=[.!?])\s+', last_chunk)
        overlap_sentences = []
        overlap_length = 0
        
        for sentence in reversed(sentences):
            if overlap_length + len(sentence) <= self.chunk_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_length += len(sentence) + 1
            else:
                break
        
        return ' '.join(overlap_sentences) if overlap_sentences else last_chunk[-self.chunk_overlap:]
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk a list of documents.
        
        Args:
            documents: List of documents with 'url', 'title', 'content'
            
        Returns:
            List of chunks with 'text' and 'metadata'
        """
        all_chunks = []
        
        for doc in documents:
            metadata = {
                'url': doc.get('url', ''),
                'title': doc.get('title', ''),
                'source': 'cloudbees_kb'
            }
            
            chunks = self.chunk_text(doc.get('content', ''), metadata)
            all_chunks.extend(chunks)
        
        return all_chunks

