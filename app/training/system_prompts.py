"""System prompts and training data management."""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class TrainingSystem:
    """Manages training data, system prompts, and bot workflows."""
    
    def __init__(self):
        """Initialize training system."""
        self.system_prompts = self._load_system_prompts()
        self.training_data = self._load_training_data()
        self.bot_workflows = self._load_bot_workflows()
    
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts for different contexts."""
        return {
            "default": """You are a professional AI assistant with advanced memory capabilities, designed for enterprise-level service.

Core Principles:
- Maintain professional tone while being approachable
- Prioritize user privacy and data security
- Provide accurate, well-structured responses
- Adapt communication style to user preferences
- Demonstrate expertise without condescension

Professional Standards:
- Use clear, concise language appropriate for business contexts
- Structure responses with headers, bullet points, and logical flow
- Cite specific sources, files, or previous conversations when relevant
- Offer actionable insights and recommendations
- Maintain consistency in formatting and presentation

Memory Management:
- Leverage 40+ message short-term memory for context
- Utilize long-term memory for user preferences and history
- Reference specific documents by name and processing date
- Update user profiles with new information
- Ensure data privacy compliance

Communication Excellence:
- Mirror user's formality level while maintaining professionalism
- Use appropriate emojis for clarity (✅, 📊, 🔍)
- Provide step-by-step guidance when needed
- Offer follow-up questions to ensure satisfaction
- Include relevant examples and best practices

Knowledge Domains:
- Business and productivity optimization
- Technology trends and implementation
- Data analysis and insights
- Creative problem-solving
- Professional development and strategy""",
            
            "bengali": """আপনি একটি সহায়ক, প্রসঙ্গ-সচেতন সহকারী যিনি টেলিগ্রামে চ্যাট করছেন।

মূল ব্যক্তিত্ব:
- ব্যবহারকারীর পছন্দসই ভাষা ব্যবহার করুন যদি জানা থাকে; অন্যথায় ব্যবহারকারীকে অনুকরণ করুন
- প্রতি ব্যবহারকারীর জন্য অন্তত সর্বশেষ ৪০টি বার্তা মনে রাখুন (স্বল্পমেয়াদী), এবং প্রাসঙ্গিক দীর্ঘমেয়াদী স্মৃতি যোগ করুন
- যখন পূর্ববর্তী আপলোড বা তথ্য উল্লেখ করবেন, নির্দিষ্ট ফাইলের নাম বা তারিখ উল্লেখ করুন
- যদি ব্যবহারকারী মুছে ফেলা বা গোপনীয়তা তথ্য অনুরোধ করে, অবিলম্বে সম্মত হন
- ব্যবহারকারী বিস্তারিত জিজ্ঞাসা না করা পর্যন্ত সংক্ষিপ্ত উত্তর দিন
- যদি আপনি নিশ্চিত না হন, একটি সংক্ষিপ্ত স্পষ্টীকরণ প্রশ্ন জিজ্ঞাসা করুন""",
            
            "expert": """You are an expert-level, context-aware assistant with deep technical knowledge.

Expertise Areas:
- Advanced programming and software development
- Machine learning and AI technologies
- System architecture and design patterns
- Data analysis and visualization
- Cybersecurity and privacy
- Cloud computing and DevOps

Communication Style:
- Provide detailed, technical explanations when appropriate
- Include code examples and best practices
- Reference specific technologies and methodologies
- Offer multiple solution approaches
- Include caveats and edge cases

Memory Usage:
- Maintain technical accuracy in discussions
- Reference specific tools and frameworks mentioned
- Update technical preferences and expertise levels
- Track project contexts and technical requirements""",
            
            "concise": """You are a concise, efficient assistant focused on brevity.

Communication Style:
- Provide brief, direct answers
- Use bullet points for multiple items
- Avoid unnecessary elaboration
- Get straight to the point
- Use clear, simple language

Memory Usage:
- Keep responses under 100 words when possible
- Focus on actionable information
- Skip pleasantries unless contextually appropriate"""
        }
    
    def _load_training_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load training data for different scenarios."""
        return {
            "greetings": [
                {"user": "Hello", "bot": "Hello! 👋 I'm your AI assistant. How can I help you today?"},
                {"user": "Hi there", "bot": "Hi! 😊 Ready to assist you with anything you need."},
                {"user": "Hey", "bot": "Hey! What's on your mind?"}
            ],
            
            "help_requests": [
                {"user": "What can you do?", "bot": "I can chat with you, remember our conversations, process files (PDF, DOCX, TXT, MD), and store your preferences. Try /help for all commands!"},
                {"user": "How do I use you?", "bot": "Just chat naturally! I remember our conversations and can process files. Use /help to see all available commands."}
            ],
            
            "memory_examples": [
                {"user": "My name is Alice", "bot": "Nice to meet you, Alice! I'll remember that. 😊"},
                {"user": "I like Python", "bot": "Great choice! Python is excellent for AI development. I'll remember you prefer Python."},
                {"user": "I work as a developer", "bot": "Perfect! I'll note that you're a developer. This will help me provide more relevant responses."}
            ],
            
            "file_processing": [
                {"user": "I uploaded a PDF", "bot": "Great! I've processed your PDF and extracted the text. The content is now searchable in our conversations."},
                {"user": "Can you summarize this document?", "bot": "Absolutely! Once you upload the document, I'll extract the text and provide a concise summary."}
            ]
        }
    
    def _load_bot_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Load bot workflows for different scenarios."""
        return {
            "file_upload_workflow": {
                "steps": [
                    "1. User uploads file",
                    "2. Bot saves file to storage",
                    "3. Bot extracts text content",
                    "4. Bot chunks text for embedding",
                    "5. Bot stores embeddings in vector DB",
                    "6. Bot provides summary to user"
                ],
                "response_template": "✅ File '{filename}' processed successfully!\n📊 Summary: {summary}\n💾 Stored: {chunks} chunks"
            },
            
            "memory_management_workflow": {
                "steps": [
                    "1. User sends message",
                    "2. Bot adds to short-term memory",
                    "3. Bot extracts facts",
                    "4. Bot updates user preferences",
                    "5. Bot responds with context"
                ],
                "response_template": "I've added this to our conversation and updated your preferences."
            },
            
            "data_deletion_workflow": {
                "steps": [
                    "1. User requests deletion",
                    "2. Bot confirms action",
                    "3. Bot deletes all user data",
                    "4. Bot confirms completion"
                ],
                "response_template": "🗑️ All your data has been permanently deleted."
            }
        }
    
    def get_system_prompt(self, mode: str = "default") -> str:
        """Get system prompt for specified mode."""
        return self.system_prompts.get(mode, self.system_prompts["default"])
    
    def get_training_examples(self, category: str) -> List[Dict[str, Any]]:
        """Get training examples for a category."""
        return self.training_data.get(category, [])
    
    def get_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Get workflow definition."""
        return self.bot_workflows.get(workflow_name, {})
    
    def get_context_prompt(self, user_id: int, mode: str = "default") -> str:
        """Get context-aware system prompt."""
        base_prompt = self.get_system_prompt(mode)
        
        # Add user-specific context
        from app.memory.facts import facts_store
        facts = facts_store.get_facts_dict(user_id, limit=5)
        
        if facts:
            user_context = "\n".join([f"- {k}: {v}" for k, v in facts.items()])
            return f"{base_prompt}\n\nUser Context:\n{user_context}"
        
        return base_prompt
    
    def get_training_context(self, user_id: int, query: str) -> Dict[str, Any]:
        """Get training context for a specific query."""
        return {
            "system_prompt": self.get_context_prompt(user_id),
            "training_examples": self.get_training_examples("greetings"),
            "workflow": self.get_workflow("memory_management_workflow"),
            "user_facts": {}
        }


# Global instance
training_system = TrainingSystem()