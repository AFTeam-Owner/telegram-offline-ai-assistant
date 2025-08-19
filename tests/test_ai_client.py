"""Tests for AI client."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from app.ai_client import AIClient


class TestAIClient:
    """Test AI client functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.client = AIClient()
        self.client.base_url = "https://api.test.com/v1"
        self.client.api_key = "test_key"
        self.client.model = "test-model"
    
    @pytest.mark.asyncio
    async def test_chat_success(self):
        """Test successful chat completion."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Hello! How can I help you?"
                    }
                }
            ]
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 200
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(
                return_value=mock_response
            )
            
            response = await self.client.chat(
                messages=[{"role": "user", "content": "Hi"}]
            )
            
            assert response == "Hello! How can I help you?"
    
    @pytest.mark.asyncio
    async def test_chat_rate_limit(self):
        """Test rate limit handling."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 429
            
            with pytest.raises(Exception, match="Rate limit exceeded"):
                await self.client.chat(
                    messages=[{"role": "user", "content": "Hi"}]
                )
    
    @pytest.mark.asyncio
    async def test_embed_success(self):
        """Test successful embedding."""
        mock_response = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]}
            ]
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 200
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(
                return_value=mock_response
            )
            
            embeddings = await self.client.embed(
                texts=["Hello", "World"]
            )
            
            assert len(embeddings) == 2
            assert len(embeddings[0]) == 3


if __name__ == "__main__":
    pytest.main([__file__])