"""User facts storage and management."""
import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.storage.db import Fact, db

logger = logging.getLogger(__name__)


class FactsStore:
    """Manages user facts and preferences."""
    
    def __init__(self):
        """Initialize facts store."""
        self.fact_extractors = [
            self._extract_name,
            self._extract_language,
            self._extract_preferences,
            self._extract_goals,
            self._extract_topics
        ]
    
    def add_fact(self, user_id: int, key: str, value: str, 
                  confidence: float = 1.0) -> None:
        """Add or update a user fact."""
        db.save_fact(user_id, key, value, confidence)
        logger.debug(f"Added fact: {user_id} -> {key} = {value}")
    
    def get_facts(self, user_id: int, limit: int = 10) -> List[Fact]:
        """Get user facts ordered by confidence."""
        return db.get_facts(user_id, limit)
    
    def get_facts_dict(self, user_id: int, limit: int = 10) -> Dict[str, str]:
        """Get facts as a dictionary."""
        facts = self.get_facts(user_id, limit)
        return {fact.key: fact.value for fact in facts}
    
    def extract_facts_from_message(self, user_id: int, message: str) -> None:
        """Extract facts from a user message."""
        for extractor in self.fact_extractors:
            try:
                facts = extractor(message)
                for key, value, confidence in facts:
                    self.add_fact(user_id, key, value, confidence)
            except Exception as e:
                logger.warning(f"Error in fact extractor: {e}")
    
    def _extract_name(self, message: str) -> List[tuple]:
        """Extract name from message."""
        patterns = [
            r"(?:my name is|i'm|i am|call me)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)",
            r"(?:this is|hi,? i'm|hello,? i'm)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)"
        ]
        
        facts = []
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                facts.append(("name", match.strip(), 0.9))
        
        return facts
    
    def _extract_language(self, message: str) -> List[tuple]:
        """Extract language preference."""
        patterns = [
            r"(?:speak|talk|chat|reply)\s+(?:in|using)\s+([a-zA-Z]+)",
            r"(?:my language is|i prefer)\s+([a-zA-Z]+)"
        ]
        
        facts = []
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                lang = match.lower()
                if lang in ["english", "bengali", "bangla", "spanish", "french", "german"]:
                    facts.append(("language", lang, 0.8))
        
        return facts
    
    def _extract_preferences(self, message: str) -> List[tuple]:
        """Extract preferences."""
        patterns = [
            (r"(?:i like|i prefer|i enjoy)\s+(.+?)(?:\.|$)", "preference"),
            (r"(?:i don't like|i hate|i dislike)\s+(.+?)(?:\.|$)", "dislike"),
            (r"(?:my favorite|my fav)\s+(.+?)(?:\.|$)", "favorite")
        ]
        
        facts = []
        for pattern, fact_type in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                facts.append((fact_type, match.strip(), 0.7))
        
        return facts
    
    def _extract_goals(self, message: str) -> List[tuple]:
        """Extract goals."""
        patterns = [
            r"(?:i want to|i need to|my goal is to|i'm trying to)\s+(.+?)(?:\.|$)",
            r"(?:help me|assist me with)\s+(.+?)(?:\.|$)"
        ]
        
        facts = []
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                facts.append(("goal", match.strip(), 0.6))
        
        return facts
    
    def _extract_topics(self, message: str) -> List[tuple]:
        """Extract topics of interest."""
        topics = [
            "programming", "python", "javascript", "ai", "machine learning",
            "data science", "web development", "mobile development",
            "design", "photography", "music", "travel", "cooking",
            "fitness", "health", "finance", "investing", "education"
        ]
        
        facts = []
        message_lower = message.lower()
        
        for topic in topics:
            if topic in message_lower:
                facts.append(("topic", topic, 0.5))
        
        return facts
    
    def delete_user_facts(self, user_id: int) -> None:
        """Delete all facts for a user."""
        # This is handled by the database when deleting user data
        logger.info(f"Deleted all facts for user {user_id}")
    
    def get_summary(self, user_id: int) -> str:
        """Get a summary of user facts."""
        facts = self.get_facts(user_id, limit=5)
        if not facts:
            return "No facts stored yet."
        
        summary_parts = []
        for fact in facts:
            summary_parts.append(f"- {fact.key}: {fact.value}")
        
        return "\n".join(summary_parts)


# Global instance
facts_store = FactsStore()