"""Rate limiting utilities - Disabled for personal use."""
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional


class RateLimiter:
    """Rate limiter for user requests - Disabled for personal use."""
    
    def __init__(self, rate_limit: int = 100, per: int = 1, burst: int = 100):
        """Initialize rate limiter - effectively disabled."""
        self.rate_limit = rate_limit
        self.per = per
        self.burst = burst
    
    async def acquire(self, user_id: int) -> bool:
        """Always allow requests for personal use."""
        return True
    
    def get_stats(self, user_id: int) -> Dict[str, int]:
        """Return dummy stats for personal use."""
        return {
            "requests_in_window": 0,
            "rate_limit": self.rate_limit,
            "window_seconds": self.per,
            "burst_limit": self.burst
        }


# Global instance - effectively disabled for personal use
rate_limiter = RateLimiter()