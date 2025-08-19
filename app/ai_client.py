"""AI client for OpenAI-compatible API."""
import asyncio
import logging
import os
from typing import List, Dict, Any, Optional

import aiohttp
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AIClient:
    """Client for OpenAI-compatible AI API."""
    
    def __init__(self):
        """Initialize AI client."""
        self.base_url = os.getenv("OPENAI_COMPAT_BASE", "https://samuraiapi.in/v1")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("MODEL_NAME", "groq/moonshotai/kimi-k2-instruct")
        
        # Debug logging
        logger.info(f"Using API endpoint: {self.base_url}")
        logger.info(f"Using model: {self.model}")
        
        # Ensure we use the configured API key
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            logger.error("Current environment variables:")
            for key, value in os.environ.items():
                if 'API' in key.upper():
                    logger.info(f"{key}: {'*' * len(value) if value else 'Not set'}")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 800,
        **kwargs
    ) -> str:
        """Send chat request to AI API."""
        model = model or self.model
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        logger.debug(f"Sending request to {self.base_url}/chat/completions")
        logger.debug(f"Headers: {dict(headers)}")
        logger.debug(f"Payload: {payload}")
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers
        ) as response:
            logger.debug(f"Response status: {response.status}")
            
            if response.status == 429:
                raise Exception("Rate limit exceeded")
            elif response.status >= 500:
                raise Exception(f"Server error: {response.status}")
            elif response.status != 200:
                error_text = await response.text()
                raise Exception(f"API error: {response.status} - {error_text}")
            
            data = await response.json()
            
            if "choices" not in data or not data["choices"]:
                raise Exception("Invalid response format")
            
            return data["choices"][0]["message"]["content"].strip()
    
    async def embed(self, texts: List[str], model: str = "groq/moonshotai/kimi-k2-instruct") -> List[List[float]]:
        """Get embeddings for texts."""
        payload = {
            "model": model,
            "input": texts
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        async with self.session.post(
            f"{self.base_url}/embeddings",
            json=payload,
            headers=headers
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Embedding API error: {response.status} - {error_text}")
            
            data = await response.json()
            
            if "data" not in data:
                raise Exception("Invalid embedding response format")
            
            return [item["embedding"] for item in data["data"]]
    
    async def health_check(self) -> bool:
        """Check if AI API is available."""
        try:
            await self.chat(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.error(f"AI API health check failed: {e}")
            return False


# Global instance
ai_client = AIClient()