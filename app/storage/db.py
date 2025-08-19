"""Database models and connection management."""
import asyncio
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.utils.tokens import count_tokens


@dataclass
class ChatMessage:
    """Represents a chat message."""
    id: str
    user_id: int
    role: str  # "user", "assistant", "system"
    content: str
    tokens: int
    created_at: datetime
    
    @classmethod
    def from_row(cls, row: tuple) -> "ChatMessage":
        """Create ChatMessage from database row."""
        return cls(
            id=row[0],
            user_id=row[1],
            role=row[2],
            content=row[3],
            tokens=row[4],
            created_at=datetime.fromisoformat(row[5])
        )


@dataclass
class User:
    """Represents a user."""
    id: int
    username: Optional[str]
    first_seen: datetime
    last_seen: datetime
    locale: Optional[str]
    
    @classmethod
    def from_row(cls, row: tuple) -> "User":
        """Create User from database row."""
        return cls(
            id=row[0],
            username=row[1],
            first_seen=datetime.fromisoformat(row[2]),
            last_seen=datetime.fromisoformat(row[3]),
            locale=row[4]
        )


@dataclass
class Fact:
    """Represents a user fact."""
    id: int
    user_id: int
    key: str
    value: str
    confidence: float
    updated_at: datetime
    
    @classmethod
    def from_row(cls, row: tuple) -> "Fact":
        """Create Fact from database row."""
        return cls(
            id=row[0],
            user_id=row[1],
            key=row[2],
            value=row[3],
            confidence=row[4],
            updated_at=datetime.fromisoformat(row[5])
        )


@dataclass
class FileRecord:
    """Represents a file record."""
    id: str
    user_id: int
    tg_file_id: str
    mime: str
    name: str
    path: str
    size: int
    created_at: datetime
    
    @classmethod
    def from_row(cls, row: tuple) -> "FileRecord":
        """Create FileRecord from database row."""
        return cls(
            id=row[0],
            user_id=row[1],
            tg_file_id=row[2],
            mime=row[3],
            name=row[4],
            path=row[5],
            size=row[6],
            created_at=datetime.fromisoformat(row[7])
        )


class Database:
    """Database connection and operations."""
    
    def __init__(self, db_path: str = "storage/app.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_tables()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_tables(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    locale TEXT
                );
                
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    tokens INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_messages_user_created 
                ON messages(user_id, created_at);
                
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, key),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_facts_user 
                ON facts(user_id);
                
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    tg_file_id TEXT NOT NULL,
                    mime TEXT NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_files_user 
                ON files(user_id);
                
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT NOT NULL,
                    chunk_id INTEGER NOT NULL,
                    vector TEXT NOT NULL,
                    text TEXT NOT NULL,
                    meta TEXT,
                    FOREIGN KEY (file_id) REFERENCES files (id),
                    UNIQUE(file_id, chunk_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_embeddings_file 
                ON embeddings(file_id);
            """)
            conn.commit()
    
    def upsert_user(self, user_id: int, username: Optional[str] = None, 
                   locale: Optional[str] = None) -> User:
        """Insert or update user."""
        now = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO users (id, username, first_seen, last_seen, locale)
                VALUES (?, COALESCE(?, (SELECT username FROM users WHERE id = ?)), 
                        COALESCE((SELECT first_seen FROM users WHERE id = ?), ?), ?, ?)
            """, (user_id, username, user_id, user_id, now, now, locale))
            conn.commit()
            
            return self.get_user(user_id)
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            )
            row = cursor.fetchone()
            return User.from_row(row) if row else None
    
    def save_message(self, message: ChatMessage) -> None:
        """Save a chat message."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO messages (id, user_id, role, content, tokens, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message.id, message.user_id, message.role, message.content, 
                  message.tokens, message.created_at.isoformat()))
            conn.commit()
    
    def get_recent_messages(self, user_id: int, limit: int = 40) -> List[ChatMessage]:
        """Get recent messages for a user."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM messages 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            return [ChatMessage.from_row(row) for row in cursor.fetchall()]
    
    def get_messages_by_tokens(self, user_id: int, max_tokens: int) -> List[ChatMessage]:
        """Get messages up to token limit."""
        messages = self.get_recent_messages(user_id, limit=1000)
        
        total_tokens = 0
        result = []
        
        for message in reversed(messages):  # Start from oldest
            if total_tokens + message.tokens > max_tokens:
                break
            result.append(message)
            total_tokens += message.tokens
        
        return result
    
    def delete_recent_messages(self, user_id: int, count: int) -> int:
        """Delete most recent messages for a user."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM messages 
                WHERE id IN (
                    SELECT id FROM messages 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                )
            """, (user_id, count))
            conn.commit()
            return cursor.rowcount
    
    def delete_all_user_data(self, user_id: int) -> None:
        """Delete all data for a user."""
        with self.get_connection() as conn:
            # Delete in correct order due to foreign keys
            conn.execute("DELETE FROM embeddings WHERE file_id IN (SELECT id FROM files WHERE user_id = ?)", (user_id,))
            conn.execute("DELETE FROM files WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM facts WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
    
    def save_fact(self, user_id: int, key: str, value: str, 
                  confidence: float = 1.0) -> None:
        """Save or update a user fact."""
        now = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO facts (user_id, key, value, confidence, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, key, value, confidence, now))
            conn.commit()
    
    def get_facts(self, user_id: int, limit: int = 10) -> List[Fact]:
        """Get user facts ordered by confidence."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM facts 
                WHERE user_id = ? 
                ORDER BY confidence DESC, updated_at DESC 
                LIMIT ?
            """, (user_id, limit))
            return [Fact.from_row(row) for row in cursor.fetchall()]
    
    def save_file(self, file_record: FileRecord) -> None:
        """Save file record."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO files (id, user_id, tg_file_id, mime, name, path, size, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (file_record.id, file_record.user_id, file_record.tg_file_id,
                  file_record.mime, file_record.name, file_record.path, 
                  file_record.size, file_record.created_at.isoformat()))
            conn.commit()
    
    def get_user_files(self, user_id: int) -> List[FileRecord]:
        """Get all files for a user."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM files 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user_id,))
            return [FileRecord.from_row(row) for row in cursor.fetchall()]
    
    def get_stats(self, user_id: int) -> Dict[str, int]:
        """Get user statistics."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM messages WHERE user_id = ?) as message_count,
                    (SELECT COUNT(*) FROM files WHERE user_id = ?) as file_count,
                    (SELECT COUNT(*) FROM facts WHERE user_id = ?) as fact_count,
                    (SELECT SUM(tokens) FROM messages WHERE user_id = ?) as total_tokens
            """, (user_id, user_id, user_id, user_id))
            row = cursor.fetchone()
            return dict(row) if row else {}


# Global database instance
db = Database()