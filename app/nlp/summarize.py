"""Text summarization utilities."""
import logging
from typing import List, Optional

from app.ai_client import ai_client

logger = logging.getLogger(__name__)


class Summarizer:
    """Handles text summarization."""
    
    def __init__(self):
        """Initialize summarizer."""
        pass
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text using AI."""
        if not text.strip():
            return ""
        
        prompt = f"""Please provide a concise summary of the following text in {max_length} characters or less:

{text}

Summary:"""
        
        try:
            response = await ai_client.chat(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length // 4
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            # Fallback to simple truncation
            return text[:max_length] + "..." if len(text) > max_length else text
    
    async def summarize_file(self, file_name: str, content: str, 
                           max_length: int = 300) -> str:
        """Summarize file content."""
        if not content.strip():
            return f"File {file_name} is empty."
        
        prompt = f"""Please provide a concise summary of this file:

File: {file_name}
Content preview: {content[:500]}...

Provide a summary in {max_length} characters or less, highlighting key points and main topics."""
        
        try:
            response = await ai_client.chat(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length // 4
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error summarizing file: {e}")
            return f"File {file_name} processed successfully."
    
    async def summarize_chunks(self, chunks: List[str], 
                           max_length: int = 400) -> str:
        """Summarize multiple chunks into a single summary."""
        if not chunks:
            return ""
        
        combined_text = "\n\n".join(chunks)
        
        if len(combined_text) <= max_length:
            return combined_text
        
        return await self.summarize_text(combined_text, max_length)


# Global instance
summarizer = Summarizer()