"""Bot workflows and training data management."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BotWorkflowManager:
    """Manages bot workflows and training data."""
    
    def __init__(self):
        """Initialize bot workflow manager."""
        self.workflows = self._load_workflows()
        self.training_data = self._load_training_data()
    
    def _load_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Load bot workflows."""
        return {
            "file_upload_workflow": {
                "name": "File Upload Processing",
                "description": "Process uploaded files and extract content",
                "steps": [
                    {
                        "step": 1,
                        "action": "Receive file upload",
                        "description": "User uploads a file (PDF, DOCX, TXT, MD)"
                    },
                    {
                        "step": 2,
                        "action": "Save file to storage",
                        "description": "Save file to ./storage/uploads/<user_id>/"
                    },
                    {
                        "step": 3,
                        "action": "Extract text content",
                        "description": "Extract text from PDF, DOCX, TXT, or MD files"
                    },
                    {
                        "step": 4,
                        "action": "Chunk text",
                        "description": "Split text into 800-1200 token chunks with 10-15% overlap"
                    },
                    {
                        "step": 5,
                        "action": "Generate embeddings",
                        "description": "Create vector embeddings for each chunk"
                    },
                    {
                        "step": 6,
                        "action": "Store in vector DB",
                        "description": "Store embeddings in ChromaDB with metadata"
                    },
                    {
                        "step": 7,
                        "action": "Provide summary",
                        "description": "Generate and provide file summary to user"
                    }
                ],
                "response_templates": {
                    "success": "✅ File '{filename}' processed successfully!\n📊 Summary: {summary}\n💾 Stored: {chunks} chunks\n🔍 Now searchable in conversations",
                    "error": "❌ Error processing file: {error}"
                }
            },
            
            "memory_management_workflow": {
                "name": "Memory Management",
                "description": "Manage user memory and context",
                "steps": [
                    {
                        "step": 1,
                        "action": "Receive message",
                        "description": "User sends a message"
                    },
                    {
                        "step": 2,
                        "action": "Add to short-term memory",
                        "description": "Store message in short-term memory (40+ messages)"
                    },
                    {
                        "step": 3,
                        "action": "Extract facts",
                        "description": "Extract key facts and preferences from message"
                    },
                    {
                        "step": 4,
                        "action": "Update user profile",
                        "description": "Update user facts and preferences"
                    },
                    {
                        "step": 5,
                        "action": "Build context",
                        "description": "Build context from memory and facts"
                    },
                    {
                        "step": 6,
                        "action": "Generate response",
                        "description": "Generate AI response with context"
                    },
                    {
                        "step": 7,
                        "action": "Store response",
                        "description": "Store AI response in memory"
                    }
                ],
                "response_templates": {
                    "context_aware": "Based on our conversation and your preferences, {response}",
                    "fact_update": "I've noted that {fact}. This will help me provide better responses."
                }
            },
            
            "data_deletion_workflow": {
                "name": "Data Deletion",
                "description": "Completely delete user data",
                "steps": [
                    {
                        "step": 1,
                        "action": "Receive deletion request",
                        "description": "User requests complete data deletion"
                    },
                    {
                        "step": 2,
                        "action": "Confirm action",
                        "description": "Confirm deletion with user"
                    },
                    {
                        "step": 3,
                        "action": "Delete short-term memory",
                        "description": "Clear short-term memory (messages)"
                    },
                    {
                        "step": 4,
                        "action": "Delete long-term memory",
                        "description": "Clear long-term memory (embeddings)"
                    },
                    {
                        "step": 5,
                        "action": "Delete user facts",
                        "description": "Remove all user facts and preferences"
                    },
                    {
                        "step": 6,
                        "action": "Delete files",
                        "description": "Remove all uploaded files"
                    },
                    {
                        "step": 7,
                        "action": "Confirm completion",
                        "description": "Confirm deletion is complete"
                    }
                ],
                "response_templates": {
                    "confirmation": "🗑️ All your data has been permanently deleted.",
                    "partial": "Deleted {items} items from your data."
                }
            },
            
            "file_search_workflow": {
                "name": "File Search and Retrieval",
                "description": "Search through uploaded files",
                "steps": [
                    {
                        "step": 1,
                        "action": "Receive search query",
                        "description": "User asks about file content"
                    },
                    {
                        "step": 2,
                        "action": "Search embeddings",
                        "description": "Search vector database for relevant content"
                    },
                    {
                        "step": 3,
                        "action": "Retrieve context",
                        "description": "Retrieve relevant file chunks and context"
                    },
                    {
                        "step": 4,
                        "action": "Generate response",
                        "description": "Generate response with file references"
                    },
                    {
                        "step": 5,
                        "action": "Provide answer",
                        "description": "Provide answer with file citations"
                    }
                ],
                "response_templates": {
                    "with_file": "Based on your uploaded file '{filename}', {answer}",
                    "without_file": "I don't have any files from you yet. Try uploading a file first!"
                }
            }
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
            ],
            
            "bengali_interactions": [
                {"user": "হ্যালো", "bot": "হ্যালো! 👋 আমি আপনার AI সহকারী। আমি কীভাবে সাহায্য করতে পারি?"},
                {"user": "আমি কীভাবে ব্যবহার করব?", "bot": "স্বাভাবিকভাবে চ্যাট করুন! আমি আমাদের কথোপকথন মনে রাখি এবং ফাইল প্রসেস করতে পারি। সব কমান্ড দেখতে /help ব্যবহার করুন।"}
            ],
            
            "technical_support": [
                {"user": "Can you help with Python?", "bot": "Absolutely! I'm well-versed in Python. Whether it's data analysis, web development, or AI/ML, I can help. What specific Python topic are you interested in?"},
                {"user": "I need help with AI", "bot": "I'd be happy to help with AI! I can assist with machine learning concepts, neural networks, or specific AI applications. What aspect of AI are you exploring?"}
            ]
        }
    
    def get_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Get workflow definition."""
        return self.workflows.get(workflow_name, {})
    
    def get_training_data(self, category: str) -> List[Dict[str, Any]]:
        """Get training data for a category."""
        return self.training_data.get(category, [])
    
    def get_personalized_training_data(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get personalized training data based on user facts."""
        from app.memory.facts import facts_store
        facts = facts_store.get_facts_dict(user_id, limit=10)
        
        training_data = self.training_data.copy()
        
        # Add personalized greetings
        if "name" in facts:
            name = facts["name"]
            training_data["personalized_greetings"] = [
                {"user": "Hello", "bot": f"Hello {name}! 👋 Nice to see you again."}
            ]
        
        # Add language-specific training
        if "language" in facts and "bengali" in facts["language"].lower():
            training_data["bengali_interactions"] = self.training_data["bengali_interactions"]
        
        # Add technical support if relevant
        if any(term in str(facts).lower() for term in ["python", "developer", "programming"]):
            training_data["technical_support"] = self.training_data["technical_support"]
        
        return training_data
    
    def get_workflow_template(self, workflow_name: str, **kwargs) -> str:
        """Get workflow template with variables."""
        workflow = self.get_workflow(workflow_name)
        template = workflow.get("response_templates", {}).get("success", "")
        return template.format(**kwargs)
    
    def get_training_summary(self, user_id: int) -> Dict[str, Any]:
        """Get training summary for a user."""
        return {
            "workflows_available": list(self.workflows.keys()),
            "training_categories": list(self.training_data.keys()),
            "personalized_data": len(self.get_personalized_training_data(user_id)),
            "total_examples": sum(len(examples) for examples in self.training_data.values())
        }


# Global instance
workflow_manager = BotWorkflowManager()