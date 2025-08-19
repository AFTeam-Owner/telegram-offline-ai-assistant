"""Telegram client implementation using Telethon."""
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from telethon import TelegramClient as TelethonClient
from telethon import events
from telethon.tl.types import UserStatusOffline

from app.storage.db import db
from app.memory.short_term import short_memory
from app.memory.long_term import long_memory
from app.memory.facts import facts_store
from app.ai_client import ai_client
from app.router import CommandRouter
from app.utils.rate_limit import rate_limiter
from app.training.system_prompts import training_system
from app.training.user_info import user_info_manager
from app.training.bot_workflows import workflow_manager
from app.config.system_data import system_data
from app.config.system_config import system_config
from app.utils.user_status import user_status_manager
from app.utils.ui_formatter import ui_formatter

logger = logging.getLogger(__name__)


class TelegramClient:
    """Main Telegram client handler."""
    
    def __init__(self):
        """Initialize Telegram client."""
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.session_name = os.getenv("TELEGRAM_SESSION_NAME", "personal_handler")
        
        self.client = TelethonClient(
            self.session_name,
            self.api_id,
            self.api_hash
        )
        
        self.router = CommandRouter()
        self.owner_id = int(os.getenv("OWNER_USER_ID", 0))
    
    async def start(self):
        """Start the Telegram client."""
        logger.info("Starting Telegram client...")
        
        await self.client.start()
        
        # Register event handlers
        self.client.add_event_handler(self.handle_new_message, events.NewMessage)
        self.client.add_event_handler(self.handle_system_config, events.NewMessage(func=lambda e: e.sender_id == self.owner_id))
        
        logger.info("Telegram client started successfully")
        
        # Run until disconnected
        await self.client.run_until_disconnected()
    
    async def handle_new_message(self, event):
        """Handle new messages with offline detection."""
        # Skip if not direct message
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        # Security: Never reply to bot's own account
        me = await self.client.get_me()
        if user_id == me.id:
            logger.info(f"Skipping message from bot's own account {user_id}")
            return
        
        # Check if should reply based on user status
        if not await user_status_manager.should_reply(self.client, user_id):
            logger.info(f"User {user_id} is offline, skipping reply")
            return
        
        # Update user info and create profile if needed
        user = await event.get_sender()
        username = user.username if user else None
        
        db.upsert_user(user_id, username)
        user_info_manager.create_user_profile(user_id, username)
        
        # Skip rate limiting for personal use
        
        # Handle commands
        message_text = event.message.message or ""
        
        if message_text.startswith('/'):
            await self.router.handle_command(event, self.client)
            return
        
        # Process regular message
        await self.process_message(event, user_id, message_text)
    
    async def process_message(self, event, user_id: int, message_text: str):
        """Process a regular message with training system integration."""
        try:
            # Security: Never process messages from bot's own account
            me = await self.client.get_me()
            if user_id == me.id:
                logger.info(f"Skipping message processing for bot's own account {user_id}")
                return
                
            # Check if user is online
            if not await user_status_manager.should_reply(self.client, user_id):
                logger.info(f"User {user_id} is offline, skipping message processing")
                return
            
            # Add to short-term memory
            short_memory.add_message(user_id, "user", message_text)
            
            # Extract facts
            facts_store.extract_facts_from_message(user_id, message_text)
            
            # Build context with training system
            context_messages = await self.build_context_with_training(user_id, message_text)
            
            # Get AI response
            response = await ai_client.chat(
                messages=context_messages,
                max_tokens=system_config.get_bot_setting("max_response_length", 800)
            )
            
            # Add response to memory
            short_memory.add_message(user_id, "assistant", response)
            
            # Send response
            await event.reply(response)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await event.reply("Sorry, I encountered an error processing your message.")
    
    # File upload functionality removed
    
    async def handle_system_config(self, event):
        """Handle system configuration updates from owner."""
        # Security: Only allow owner account to access system config
        if event.sender_id != self.owner_id:
            return
        
        message_text = event.message.message or ""
        
        # Handle configuration updates
        if message_text.startswith('/config'):
            await self.handle_config_command(event)
            return
        
        # Handle direct file uploads for configuration
        if event.media and event.sender_id == self.owner_id:
            await self.handle_config_file_upload(event)
            return
    
    async def handle_config_command(self, event):
        """Handle configuration commands from owner."""
        message_text = event.message.message or ""
        parts = message_text.split()
        
        if len(parts) < 2:
            await event.reply(ui_formatter.format_command_help())
            return
        
        command = parts[1]
        
        if command == "start":
            system_config.update_bot_setting("auto_reply_enabled", True)
            await event.reply(ui_formatter.format_success("Auto-reply enabled"))
        
        elif command == "stop":
            system_config.update_bot_setting("auto_reply_enabled", False)
            await event.reply(ui_formatter.format_success("Auto-reply disabled"))
        
        elif command == "status":
            enabled = system_config.get_bot_setting("auto_reply_enabled", True)
            config = system_config.current_config["bot_settings"]
            await event.reply(ui_formatter.format_status_report(enabled, config))
        
        elif command == "reload":
            system_data.reset_to_default()
            await event.reply(ui_formatter.format_config_updated("Configuration reloaded to defaults"))
        
        elif command == "reset":
            system_data.reset_to_default()
            await event.reply(ui_formatter.format_config_updated("Configuration reset to defaults"))
    
    async def handle_config_file_upload(self, event):
        """Handle configuration file uploads from owner."""
        if not event.media or event.sender_id != self.owner_id:
            return
        
        try:
            file_data = await event.download_media(bytes)
            file_name = "config_update.txt"
            
            # Save configuration file
            config_path = Path("config") / file_name
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'wb') as f:
                f.write(file_data)
            
            # Load configuration from file
            if system_data.load_from_txt_file(str(config_path)):
                await event.reply("✅ Configuration updated from file")
            else:
                await event.reply("❌ Could not load configuration from file")
                
        except Exception as e:
            logger.error(f"Error handling config file upload: {e}")
            await event.reply("❌ Error processing configuration file")
    
    async def build_context_with_training(self, user_id: int, current_message: str) -> list:
        """Build context with training system integration."""
        # Get dynamic system prompt
        system_prompt = system_data.get_system_prompt("default")
        
        # Get user training context
        training_context = user_info_manager.get_user_training_context(user_id)
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add user facts
        facts = training_context["facts"]
        if facts:
            facts_text = "\n".join([f"- {k}: {v}" for k, v in facts.items()])
            messages.append({
                "role": "system", 
                "content": f"User Context:\n{facts_text}"
            })
        
        # Add recent messages
        recent_messages = short_memory.get_context_messages(user_id)
        for msg in recent_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add long-term memory
        memories = long_memory.search(user_id, current_message, top_k=5)
        if memories:
            memory_text = "\n\n".join([m.text for m in memories])
            messages.append({
                "role": "system",
                "content": f"Relevant memories:\n{memory_text}"
            })
        
        # Add training examples if relevant
        training_examples = training_context.get("training_data", {})
        if "greetings" in training_examples:
            # Add context about training
            messages.append({
                "role": "system",
                "content": "Training examples available for greetings and common interactions."
            })
        
        # Current message
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get training summary."""
        return {
            "system_data": system_data.get_config_summary(),
            "training_system": "training_system_loaded",
            "user_status": "online_detection_enabled",
            "config_files": {
                "system_data": str(system_data.system_data_file),
                "prompts": str(system_data.prompts_file),
                "workflows": str(system_data.workflows_file)
            }
        }