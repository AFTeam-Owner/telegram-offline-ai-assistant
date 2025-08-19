"""Long-term memory management with vector storage."""
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.storage.db import db
from app.utils.tokens import count_tokens, split_into_chunks

logger = logging.getLogger(__name__)


@dataclass
class MemorySummary:
    """Represents a memory summary."""
    source: str  # "recent", "vector", "facts"
    text: str
    score: float
    meta: Dict[str, Any]


class LongTermMemory:
    """Manages long-term memory with vector storage."""
    
    def __init__(self, persist_dir: str = "./storage/chroma"):
        """Initialize long-term memory."""
        self.persist_dir = persist_dir
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        os.makedirs(persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collections
        self.messages_collection = self.client.get_or_create_collection(
            name="messages",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.files_collection = self.client.get_or_create_collection(
            name="files",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_message(self, user_id: int, content: str, 
                    message_id: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to long-term memory."""
        embedding = self.embeddings_model.encode([content])[0].tolist()
        
        doc_id = f"{user_id}_{message_id}"
        meta = {
            "user_id": user_id,
            "type": "message",
            "created_at": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        self.messages_collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta],
            ids=[doc_id]
        )
        
        logger.debug(f"Added message to long-term memory: {doc_id}")
    
    def add_file_chunks(self, user_id: int, file_id: str, chunks: List[str],
                       file_name: str, metadata: Optional[Dict] = None) -> None:
        """Add file chunks to long-term memory."""
        if not chunks:
            return
        
        embeddings = self.embeddings_model.encode(chunks)
        
        ids = []
        documents = []
        metadatas = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_id = f"{user_id}_{file_id}_{i}"
            meta = {
                "user_id": user_id,
                "file_id": file_id,
                "chunk_id": i,
                "type": "file_chunk",
                "file_name": file_name,
                "created_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            ids.append(doc_id)
            documents.append(chunk)
            metadatas.append(meta)
        
        self.files_collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks for file {file_id}")
    
    def search(self, user_id: int, query: str, top_k: int = 6) -> List[MemorySummary]:
        """Search long-term memory for relevant content."""
        query_embedding = self.embeddings_model.encode([query])[0].tolist()
        
        # Search messages
        message_results = self.messages_collection.query(
            query_embeddings=[query_embedding],
            where={"user_id": user_id},
            n_results=top_k // 2
        )
        
        # Search files
        file_results = self.files_collection.query(
            query_embeddings=[query_embedding],
            where={"user_id": user_id},
            n_results=top_k // 2
        )
        
        summaries = []
        
        # Process message results
        if message_results['documents']:
            for doc, meta, score in zip(
                message_results['documents'][0],
                message_results['metadatas'][0],
                message_results['distances'][0]
            ):
                summaries.append(MemorySummary(
                    source="vector",
                    text=doc,
                    score=1.0 - score,  # Convert distance to similarity
                    meta=meta
                ))
        
        # Process file results
        if file_results['documents']:
            for doc, meta, score in zip(
                file_results['documents'][0],
                file_results['metadatas'][0],
                file_results['distances'][0]
            ):
                summaries.append(MemorySummary(
                    source="vector",
                    text=doc,
                    score=1.0 - score,
                    meta=meta
                ))
        
        # Sort by score and return top-k
        summaries.sort(key=lambda x: x.score, reverse=True)
        return summaries[:top_k]
    
    def get_user_memories(self, user_id: int, limit: int = 100) -> List[MemorySummary]:
        """Get all memories for a user."""
        # Get messages
        message_results = self.messages_collection.get(
            where={"user_id": user_id},
            limit=limit // 2
        )
        
        # Get file chunks
        file_results = self.files_collection.get(
            where={"user_id": user_id},
            limit=limit // 2
        )
        
        summaries = []
        
        # Process messages
        for doc, meta in zip(message_results['documents'], message_results['metadatas']):
            summaries.append(MemorySummary(
                source="vector",
                text=doc,
                score=1.0,
                meta=meta
            ))
        
        # Process files
        for doc, meta in zip(file_results['documents'], file_results['metadatas']):
            summaries.append(MemorySummary(
                source="vector",
                text=doc,
                score=1.0,
                meta=meta
            ))
        
        return summaries
    
    def delete_user_memories(self, user_id: int) -> None:
        """Delete all memories for a user."""
        # Delete from messages collection
        message_results = self.messages_collection.get(
            where={"user_id": user_id}
        )
        if message_results['ids']:
            self.messages_collection.delete(ids=message_results['ids'])
        
        # Delete from files collection
        file_results = self.files_collection.get(
            where={"user_id": user_id}
        )
        if file_results['ids']:
            self.files_collection.delete(ids=file_results['ids'])
        
        logger.info(f"Deleted all long-term memories for user {user_id}")
    
    def get_stats(self, user_id: int) -> Dict[str, int]:
        """Get memory statistics."""
        try:
            message_count = len(self.messages_collection.get(
                where={"user_id": user_id}
            )['ids'])
            
            file_count = len(self.files_collection.get(
                where={"user_id": user_id}
            )['ids'])
            
            return {
                "message_memories": message_count,
                "file_chunks": file_count
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"message_memories": 0, "file_chunks": 0}


# Global instance
long_memory = LongTermMemory()