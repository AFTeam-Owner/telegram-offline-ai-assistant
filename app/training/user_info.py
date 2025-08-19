"""User information management and training data."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.storage.db import db
from app.memory.facts import facts_store

logger = logging.getLogger(__name__)


class UserInfoManager:
    """Manages user information and training data."""
    
    def __init__(self):
        """Initialize user info manager."""
        self.user_profiles = {}
    
    def create_user_profile(self, user_id: int, username: Optional[str] = None) -> Dict[str, Any]:
        """Create a comprehensive user profile."""
        profile = {
            "user_id": user_id,
            "username": username,
            "first_seen": datetime.now(),
            "last_seen": datetime.now(),
            "preferences": {},
            "skills": [],
            "goals": [],
            "topics": [],
            "language": "auto",
            "communication_style": "friendly",
            "expertise_level": "intermediate"
        }
        
        # Save to database
        db.upsert_user(user_id, username)
        
        # Initialize facts
        facts_store.add_fact(user_id, "profile_created", "true", 1.0)
        
        return profile
    
    def update_user_preference(self, user_id: int, key: str, value: str, confidence: float = 1.0):
        """Update user preference."""
        facts_store.add_fact(user_id, f"preference_{key}", value, confidence)
    
    def get_user_training_context(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive training context for a user."""
        # Get user facts
        facts = facts_store.get_facts_dict(user_id, limit=20)
        
        # Build training context
        context = {
            "user_id": user_id,
            "facts": facts,
            "preferences": self._extract_preferences(facts),
            "communication_style": self._detect_communication_style(facts),
            "expertise_level": self._detect_expertise_level(facts),
            "language_preference": self._detect_language_preference(facts),
            "training_data": self._get_personalized_training_data(facts)
        }
        
        return context
    
    def _extract_preferences(self, facts: Dict[str, str]) -> Dict[str, str]:
        """Extract user preferences from facts."""
        preferences = {}
        for key, value in facts.items():
            if key.startswith("preference_"):
                pref_key = key.replace("preference_", "")
                preferences[pref_key] = value
        return preferences
    
    def _detect_communication_style(self, facts: Dict[str, str]) -> str:
        """Detect user's preferred communication style."""
        style_indicators = {
            "communication_style": "friendly",
            "tone": "casual",
            "formality": "medium"
        }
        
        # Check for explicit preferences
        if "communication_style" in facts:
            return facts["communication_style"]
        
        # Detect from language preferences
        if "language" in facts and "bengali" in facts["language"].lower():
            return "bengali"
        
        return "friendly"
    
    def _detect_expertise_level(self, facts: Dict[str, str]) -> str:
        """Detect user's expertise level."""
        level_indicators = {
            "expertise": "intermediate",
            "experience": "medium",
            "skill_level": "intermediate"
        }
        
        # Check for explicit expertise
        if "expertise_level" in facts:
            return facts["expertise_level"]
        
        # Detect from technical facts
        technical_terms = ["python", "javascript", "ai", "ml", "programming", "developer"]
        for term in technical_terms:
            if term in str(facts).lower():
                return "advanced"
        
        return "intermediate"
    
    def _detect_language_preference(self, facts: Dict[str, str]) -> str:
        """Detect user's language preference."""
        if "language" in facts:
            return facts["language"]
        
        return "auto"
    
    def _get_personalized_training_data(self, facts: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """Get personalized training data based on user facts."""
        training_data = {
            "greetings": [
                {"user": "Hello", "bot": "Hello! 👋 I'm your AI assistant. How can I help you today?"},
                {"user": "Hi there", "bot": "Hi! 😊 Ready to assist you with anything you need."},
                {"user": "Hey", "bot": "Hey! What's on your mind?"}
            ],
            
            "personalized_greetings": self._generate_personalized_greetings(facts),
            
            "help_requests": [
                {"user": "What can you do?", "bot": "I can chat with you, remember our conversations, process files (PDF, DOCX, TXT, MD), and store your preferences. Try /help for all commands!"},
                {"user": "How do I use you?", "bot": "Just chat naturally! I remember our conversations and can process files. Use /help to see all available commands."}
            ],
            
            "memory_examples": [
                {"user": "My name is Alice", "bot": "Nice to meet you, Alice! I'll remember that. 😊"},
                {"user": "I like Python", "bot": "Great choice! Python is excellent for AI development. I'll remember you prefer Python."},
                {"user": "I work as a developer", "bot": "Perfect! I'll note that you're a developer. This will help me provide more relevant responses."}
            ],
            
            "technical_support": self._generate_technical_support(facts),
            
            "file_processing": [
                {"user": "I uploaded a PDF", "bot": "Great! I've processed your PDF and extracted the text. The content is now searchable in our conversations."},
                {"user": "Can you summarize this document?", "bot": "Absolutely! Once you upload the document, I'll extract the text and provide a concise summary."}
            ]
        }
        
        return training_data
    
    def _generate_personalized_greetings(self, facts: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate personalized greetings based on user facts."""
        greetings = []
        
        if "name" in facts:
            name = facts["name"]
            greetings.append({"user": "Hello", "bot": f"Hello {name}! 👋 Nice to see you again."})
        
        if "language" in facts and "bengali" in facts["language"].lower():
            greetings.append({"user": "Hello", "bot": "হ্যালো! 👋 আমি আপনার AI সহকারী। আমি কীভাবে সাহায্য করতে পারি?"})
        
        return greetings
    
    def _generate_technical_support(self, facts: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate technical support based on user expertise."""
        support = []
        
        if any(term in str(facts).lower() for term in ["python", "developer", "programming"]):
            support.append({
                "user": "Can you help with Python?",
                "bot": "Absolutely! I'm well-versed in Python. Whether it's data analysis, web development, or AI/ML, I can help. What specific Python topic are you interested in?"
            })
        
        return support
    
    def get_training_context(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive training context."""
        context = self.get_user_training_context(user_id)
        
        # Add system prompt
        context["system_prompt"] = self._build_dynamic_system_prompt(context)
        
        return context
    
    def _build_dynamic_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build dynamic system prompt based on user context."""
        base_prompt = """You are a helpful, context-aware assistant chatting in Telegram.

Core Instructions:
- Always use the user's preferred language if known; else mirror the user
- Remember at least the last 40 messages per user (short-term), and augment with relevant long-term memory
- When referring to earlier uploads or facts, be specific and cite the file name or date
- If the user requests deletion or privacy info, comply immediately
- Keep answers concise unless the user asks for detail
- If you're unsure, ask a brief clarifying question

User Context:
"""
        
        # Add user-specific context
        if context["preferences"]:
            base_prompt += f"\nUser Preferences: {context['preferences']}"
        
        if context["language_preference"] != "auto":
            base_prompt += f"\nLanguage: {context['language_preference']}"
        
        if context["expertise_level"] != "intermediate":
            base_prompt += f"\nExpertise Level: {context['expertise_level']}"
        
        return base_prompt
    
    def add_training_example(self, user_id: int, user_input: str, bot_response: str):
        """Add a training example for this user."""
        # Store as a fact for this user
        facts_store.add_fact(user_id, f"training_example_{hash(user_input)}", bot_response, 0.8)
    
    def get_user_training_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of user's training data."""
        context = self.get_user_training_context(user_id)
        
        return {
            "user_id": user_id,
            "total_facts": len(context["facts"]),
            "preferences": context["preferences"],
            "communication_style": context["communication_style"],
            "training_examples_count": len(context["training_data"]["greetings"]),
            "system_prompt_length": len(context["system_prompt"])
        }


# Global instance
user_info_manager = UserInfoManager()