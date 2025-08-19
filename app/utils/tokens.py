"""Token utilities for text processing and sanitization."""
import re
from typing import List, Tuple

import tiktoken


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        # Fallback to cl100k_base encoding
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


def truncate_by_tokens(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """Truncate text to fit within token limit."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    
    if len(tokens) <= max_tokens:
        return text
    
    # Truncate from the beginning to keep the end
    truncated_tokens = tokens[-max_tokens:]
    return encoding.decode(truncated_tokens)


def sanitize_for_logging(text: str) -> str:
    """Remove sensitive information from text for logging."""
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove API keys
    text = re.sub(r'(?i)(api[_-]?key|token|secret)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', r'\1=[REDACTED]', text)
    
    # Remove URLs with sensitive data
    text = re.sub(r'https?://[^\s]+', '[URL]', text)
    
    return text


def split_into_chunks(text: str, max_tokens: int, model: str = "gpt-4") -> List[str]:
    """Split text into chunks that fit within token limit."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = start + max_tokens
        
        # Try to break at sentence boundaries
        if end < len(tokens):
            # Look for sentence endings
            chunk_tokens = tokens[start:end]
            chunk_text = encoding.decode(chunk_tokens)
            
            # Find last sentence ending
            last_period = chunk_text.rfind('. ')
            if last_period > len(chunk_text) * 0.7:  # Only if we have enough content
                end = start + len(encoding.encode(chunk_text[:last_period + 1]))
        
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start = end
    
    return chunks


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 chars)."""
    return len(text) // 4