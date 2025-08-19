"""File handling and processing utilities."""
import asyncio
import logging
import mimetypes
import os
import uuid
from pathlib import Path
from typing import Optional, List

import aiofiles
from pypdf import PdfReader
from docx import Document

from app.storage.db import FileRecord, db
from app.nlp.chunk import chunker
from app.nlp.summarize import summarizer
from app.memory.long_term import long_memory
from app.utils.tokens import count_tokens

logger = logging.getLogger(__name__)


class FileProcessor:
    """Handles file processing and storage."""
    
    def __init__(self):
        """Initialize file processor."""
        self.upload_dir = Path("storage/uploads")
        self.max_file_size = int(os.getenv("MAX_FILE_MB", 10)) * 1024 * 1024
        self.allowed_types = os.getenv("ALLOWED_FILE_TYPES", "pdf,docx,txt,md").split(",")
    
    async def save_file(self, user_id: int, tg_file_id: str, file_name: str,
                       mime_type: str, file_data: bytes) -> Optional[FileRecord]:
        """Save uploaded file and process it."""
        if len(file_data) > self.max_file_size:
            raise ValueError(f"File too large. Max size: {self.max_file_size // 1024 // 1024}MB")
        
        # Create user directory
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = user_dir / f"{file_id}_{file_name}"
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)
        
        # Create file record
        file_record = FileRecord(
            id=file_id,
            user_id=user_id,
            tg_file_id=tg_file_id,
            mime=mime_type,
            name=file_name,
            path=str(file_path),
            size=len(file_data),
            created_at=datetime.now()
        )
        
        db.save_file(file_record)
        
        # Process file content
        try:
            content = await self._extract_content(file_path, mime_type)
            if content:
                await self._process_content(user_id, file_id, file_name, content)
        except Exception as e:
            logger.error(f"Error processing file {file_name}: {e}")
        
        return file_record
    
    async def _extract_content(self, file_path: Path, mime_type: str) -> Optional[str]:
        """Extract text content from file."""
        try:
            if mime_type == "application/pdf":
                return self._extract_pdf(file_path)
            elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                             "application/msword"]:
                return self._extract_docx(file_path)
            elif mime_type.startswith("text/"):
                return self._extract_text(file_path)
            else:
                logger.warning(f"Unsupported file type: {mime_type}")
                return None
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return None
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF."""
        reader = PdfReader(file_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX."""
        doc = Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    
    def _extract_text(self, file_path: Path) -> str:
        """Extract text from text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def _process_content(self, user_id: int, file_id: str, 
                             file_name: str, content: str) -> None:
        """Process file content for indexing."""
        # Chunk the content
        chunks = chunker.chunk_text(content)
        
        if not chunks:
            return
        
        # Add to vector memory
        long_memory.add_file_chunks(
            user_id=user_id,
            file_id=file_id,
            chunks=chunks,
            file_name=file_name,
            metadata={"source": "upload", "file_name": file_name}
        )
        
        # Generate summary
        summary = await summarizer.summarize_file(file_name, content)
        
        logger.info(f"Processed file {file_name}: {len(chunks)} chunks, {count_tokens(content)} tokens")
    
    def get_user_files(self, user_id: int) -> List[FileRecord]:
        """Get all files for a user."""
        return db.get_user_files(user_id)
    
    def delete_user_files(self, user_id: int) -> None:
        """Delete all files for a user."""
        files = self.get_user_files(user_id)
        
        for file_record in files:
            file_path = Path(file_record.path)
            if file_path.exists():
                file_path.unlink()
        
        logger.info(f"Deleted all files for user {user_id}")
    
    def get_file_stats(self, user_id: int) -> dict:
        """Get file statistics for a user."""
        files = self.get_user_files(user_id)
        
        total_size = sum(f.size for f in files)
        file_types = {}
        
        for file in files:
            ext = Path(file.name).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "file_count": len(files),
            "total_size": total_size,
            "file_types": file_types
        }


# Global instance
file_processor = FileProcessor()