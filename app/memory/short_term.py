"""Short-term memory management with sliding window."""
import logging
from datetime import datetime
from typing import List, Optional

from app.storage.db import ChatMessage, db
from app.utils.tokens import count_tokens

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """Manages short-term conversation memory."""
    
    def __init__(self, max_messages: int = 40, token_budget: int = 6000):
        """
        Initialize short-term memory.
        
        Args:
            max_messages: Maximum number of messages to keep
            token_budget: Maximum tokens to use for context
        """
        self.max_messages = max_messages
        self.token_budget = token_budget
    
    def add_message(self, user_id: int, role: str, content: str, 
                    message_id: Optional[str] = None) -> ChatMessage:
        """Add a message to short-term memory."""
        if message_id is None:
            message_id = f"{user_id}_{datetime.now().isoformat()}"
        
        tokens = count_tokens(content)
        message = ChatMessage(
            id=message_id,
            user_id=user_id,
            role=role,
            content=content,
            tokens=tokens,
            created_at=datetime.now()
        )
        
        db.save_message(message)
        logger.debug(f"Added message to short-term memory: {message_id}")
        return message
    
    def get_recent_messages(self, user_id: int, limit: Optional[int] = None) -> List[ChatMessage]:
        """Get recent messages for a user."""
        limit = limit or self.max_messages
        messages = db.get_recent_messages(user_id, limit=limit)
        
        # Return in chronological order (oldest first)
        return list(reversed(messages))
    
    def get_context_messages(self, user_id: int) -> List[ChatMessage]:
        """Get messages for AI context, respecting token budget."""
        messages = db.get_messages_by_tokens(user_id, self.token_budget)
        
        # Ensure we have at least some context
        if not messages:
            messages = self.get_recent_messages(user_id, limit=10)
        
        return messages
    
    def forget_last(self, user_id: int, count: int = 10) -> int:
        """Forget the last N messages."""
        deleted = db.delete_recent_messages(user_id, count)
        logger.info(f"Forgot {deleted} messages for user {user_id}")
        return deleted
    
    def forget_all(self, user_id: int) -> None:
        """Forget all messages for a user."""
        deleted = db.delete_recent_messages(user_id, 10000)  # Large number
        logger.info(f"Cleared all short-term memory for user {user_id}")
    
    def get_stats(self, user_id: int) -> dict:
        """Get memory statistics."""
        messages = self.get_recent_messages(user_id)
        total_tokens = sum(msg.tokens for msg in messages)
        
        return {
            "message_count": len(messages),
            "total_tokens": total_tokens,
            "max_messages": self.max_messages,
            "token_budget": self.token_budget,
            "utilization": total_tokens / self.token_budget if self.token_budget > 0 else 0
        }


# Global instance
short_memory = ShortTermMemory()