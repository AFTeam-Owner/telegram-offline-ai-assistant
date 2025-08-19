"""Text chunking utilities for processing documents."""
import logging
from typing import List

from app.utils.tokens import count_tokens, split_into_chunks

logger = logging.getLogger(__name__)


class TextChunker:
    """Handles text chunking for document processing."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target size for each chunk in tokens
            overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return []
        
        chunks = split_into_chunks(
            text, 
            max_tokens=self.chunk_size,
            overlap=self.overlap
        )
        
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def chunk_with_context(self, text: str, context_size: int = 200) -> List[dict]:
        """Chunk text with surrounding context."""
        chunks = self.chunk_text(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            # Get context from previous chunks
            start_context = ""
            if i > 0:
                prev_chunk = chunks[i-1]
                tokens = prev_chunk.split()
                start_context = " ".join(tokens[-context_size//2:])
            
            # Get context from next chunks
            end_context = ""
            if i < len(chunks) - 1:
                next_chunk = chunks[i+1]
                tokens = next_chunk.split()
                end_context = " ".join(tokens[:context_size//2])
            
            result.append({
                "chunk": chunk,
                "context": f"{start_context} ... {end_context}".strip(),
                "chunk_id": i,
                "tokens": count_tokens(chunk)
            })
        
        return result


# Global instance
chunker = TextChunker()