"""User status management for offline detection."""
import logging
from datetime import datetime, timedelta
from typing import Optional

from telethon import TelegramClient
from telethon.tl.types import UserStatusOffline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth
from app.config.system_config import system_config

logger = logging.getLogger(__name__)


class UserStatusManager:
    """Manages user online/offline status detection."""
    
    def __init__(self):
        """Initialize user status manager."""
        self.offline_threshold = timedelta(minutes=5)
    
    async def should_reply(self, client: TelegramClient, user_id: int) -> bool:
        """
        Check if we should reply based on bot's online status and owner control.
        
        Args:
            client: Telegram client instance
            user_id: User ID to check
            
        Returns:
            True when auto-reply is enabled and bot is offline
        """
        try:
            # Check if auto-reply is enabled
            if not system_config.get_bot_setting("auto_reply_enabled", True):
                logger.info("Auto-reply disabled by owner")
                return False
            
            # Check if bot account is online - only reply when bot is offline
            me = await client.get_me()
            bot_status = await client.get_entity(me.id)
            
            # If bot account is online, don't reply
            if hasattr(bot_status, 'status') and bot_status.status is None:
                logger.info("Bot account is online, disabling auto-reply")
                return False
            
            # Bot is offline and auto-reply is enabled
            logger.info("Bot account is offline and auto-reply enabled")
            return True
            
        except Exception as e:
            logger.warning(f"Could not check bot status: {e}")
            # Default to allow reply if we can't determine status
            return True
    
    async def get_user_status(self, client: TelegramClient, user_id: int) -> str:
        """
        Get human-readable user status.
        
        Args:
            client: Telegram client instance
            user_id: User ID to check
            
        Returns:
            String describing user status
        """
        try:
            user = await client.get_entity(user_id)
            
            if not hasattr(user, 'status') or not user.status:
                return "Unknown"
            
            status = user.status
            
            if status is None:
                return "Online"
            elif isinstance(status, UserStatusOffline):
                return f"Offline since {status.was_online}"
            elif isinstance(status, UserStatusRecently):
                return "Recently active"
            elif isinstance(status, UserStatusLastWeek):
                return "Active last week"
            elif isinstance(status, UserStatusLastMonth):
                return "Active last month"
            else:
                return "Unknown"
                
        except Exception as e:
            logger.warning(f"Could not get user status for {user_id}: {e}")
            return "Unknown"


# Global instance
user_status_manager = UserStatusManager()