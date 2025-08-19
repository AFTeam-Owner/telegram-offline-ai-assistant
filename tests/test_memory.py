"""Tests for memory management."""
import pytest
from datetime import datetime

from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.memory.facts import FactsStore
from app.storage.db import db


class TestShortTermMemory:
    """Test short-term memory functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.memory = ShortTermMemory(max_messages=5, token_budget=1000)
        self.user_id = 12345
    
    def test_add_message(self):
        """Test adding messages to memory."""
        message = self.memory.add_message(self.user_id, "user", "Hello world")
        
        assert message.user_id == self.user_id
        assert message.role == "user"
        assert message.content == "Hello world"
        assert message.tokens > 0
    
    def test_get_recent_messages(self):
        """Test retrieving recent messages."""
        # Add multiple messages
        for i in range(3):
            self.memory.add_message(self.user_id, "user", f"Message {i}")
        
        messages = self.memory.get_recent_messages(self.user_id)
        
        assert len(messages) == 3
        assert all(m.user_id == self.user_id for m in messages)
    
    def test_forget_last(self):
        """Test forgetting messages."""
        # Add messages
        for i in range(5):
            self.memory.add_message(self.user_id, "user", f"Message {i}")
        
        # Forget 2 messages
        deleted = self.memory.forget_last(self.user_id, 2)
        assert deleted == 2
        
        # Check remaining messages
        messages = self.memory.get_recent_messages(self.user_id)
        assert len(messages) == 3


class TestFactsStore:
    """Test facts storage functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.store = FactsStore()
        self.user_id = 12345
    
    def test_add_fact(self):
        """Test adding facts."""
        self.store.add_fact(self.user_id, "name", "Alice", 0.9)
        
        facts = self.store.get_facts(self.user_id)
        assert len(facts) == 1
        assert facts[0].key == "name"
        assert facts[0].value == "Alice"
        assert facts[0].confidence == 0.9
    
    def test_extract_facts(self):
        """Test fact extraction from messages."""
        message = "My name is Bob and I like Python programming"
        self.store.extract_facts_from_message(self.user_id, message)
        
        facts = self.store.get_facts_dict(self.user_id)
        assert "name" in facts
        assert "topic" in facts


class TestLongTermMemory:
    """Test long-term memory functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.memory = LongTermMemory(persist_dir="./test_chroma")
        self.user_id = 12345
    
    def test_add_and_search(self):
        """Test adding and searching memories."""
        # Add a memory
        self.memory.add_message(
            self.user_id,
            "I love machine learning and AI",
            "test_msg_1"
        )
        
        # Search for relevant content
        results = self.memory.search(self.user_id, "machine learning", top_k=1)
        
        assert len(results) > 0
        assert "machine learning" in results[0].text.lower()