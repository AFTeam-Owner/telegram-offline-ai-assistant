"""Command router for handling Telegram commands."""
import logging
import os
from datetime import datetime

from telethon import TelegramClient

from app.storage.db import db
from app.memory.short_term import short_memory
from app.memory.long_term import long_memory
from app.memory.facts import facts_store
from app.storage.files import file_processor
from app.nlp.summarize import summarizer

logger = logging.getLogger(__name__)


class CommandRouter:
    """Routes and handles Telegram commands."""
    
    def __init__(self):
        """Initialize command router."""
        self.owner_id = int(os.getenv("OWNER_USER_ID", 0))
    
    async def handle_command(self, event, client: TelegramClient):
        """Handle incoming commands."""
        message = event.message
        user_id = event.sender_id
        text = message.message or ""
        
        # Parse command
        parts = text.split()
        command = parts[0].lower()
        args = parts[1:]
        
        # Route command
        if command == "/start":
            await self._handle_start(event)
        elif command == "/help":
            await self._handle_help(event)
        elif command == "/memory":
            await self._handle_memory(event, user_id)
        elif command == "/forget":
            await self._handle_forget(event, user_id, args)
        elif command == "/forget_all":
            await self._handle_forget_all(event, user_id)
        elif command == "/wipe_me":
            await self._handle_wipe_me(event, user_id)
        elif command == "/export":
            await self._handle_export(event, user_id)
        elif command == "/mode":
            await self._handle_mode(event, user_id, args)
        elif command == "/stats":
            await self._handle_stats(event, user_id)
        elif command == "/privacy":
            await self._handle_privacy(event)
        elif command == "/admin" and user_id == self.owner_id:
            await self._handle_admin(event)
        else:
            await event.reply("Unknown command. Type /help for available commands.")
    
    async def _handle_start(self, event):
        """Handle /start command with professional UI."""
        welcome_text = """🤖 **Welcome to Your AI Assistant**

I'm your intelligent companion with advanced memory capabilities.

**✨ Core Features:**
• **Conversational Memory** – Remembers context across 40+ messages
• **File Intelligence** – Process PDF, DOCX, TXT, MD files with AI analysis
• **Personal Learning** – Adapts to your preferences and communication style
• **Privacy-First** – Your data stays local and encrypted

**📋 Quick Start:**
1. Send a message to begin chatting
2. Upload any file for intelligent processing
3. Use commands below to explore features

**🎯 Available Commands:**
`/help` - Complete command guide
`/memory` - View stored memories
`/stats` - Usage analytics
`/privacy` - Data protection info

**💡 Pro Tip:** Start with a simple greeting or upload a document to see my capabilities in action!"""
        
        await event.reply(welcome_text)
    
    async def _handle_help(self, event):
        """Handle /help command with professional formatting."""
        help_text = """📖 **Complete Command Guide**

**🚀 Getting Started:**
`/start` - Welcome & feature overview

**🧠 Memory Management:**
`/memory` - View your stored memories & facts
`/forget [n]` - Remove last n messages (default: 10)
`/forget_all` - Clear short-term memory

**📊 Data Control:**
`/wipe_me` - **Permanently delete** all your data
`/export` - Download your complete data archive

**⚙️ Personalization:**
`/mode [style]` - Customize AI personality:
• `concise` - Brief, efficient responses
• `friendly` - Warm, conversational tone
• `expert` - Technical, detailed answers
• `bengali-first` - Bengali language priority

**📈 Analytics:**
`/stats` - Usage statistics & insights
`/privacy` - Data protection & rights

**📁 File Processing:**
Simply upload any file (PDF, DOCX, TXT, MD) for AI analysis

**💡 Examples:**
`/mode expert`
`/forget 15`
`/export`

**Need help?** Just ask - I'm here to assist!"""
        
        await event.reply(help_text)
    
    async def _handle_memory(self, event, user_id: int):
        """Handle /memory command with professional dashboard."""
        # Get all memory stats
        short_stats = short_memory.get_stats(user_id)
        long_stats = long_memory.get_stats(user_id)
        facts = facts_store.get_facts(user_id, limit=10)
        
        response = """🧠 **Memory Dashboard**

**📊 Memory Overview:**
• **Short-term**: {short_msg} messages ({short_tokens} tokens)
• **Long-term**: {long_msg} messages, {long_chunks} file chunks
• **Facts stored**: {fact_count} personal insights

**🔍 Personal Insights:""".format(
            short_msg=short_stats['message_count'],
            short_tokens=short_stats['total_tokens'],
            long_msg=long_stats['message_memories'],
            long_chunks=long_stats['file_chunks'],
            fact_count=len(facts)
        )
        
        if facts:
            for i, fact in enumerate(facts[:5], 1):
                response += f"\n{i}. **{fact.key.title()}**: {fact.value}"
        
        response += "\n\n**💡 Memory Management:**\nUse `/forget [n]` to manage your memory efficiently"
        
        await event.reply(response)
    
    async def _handle_forget(self, event, user_id: int, args: list):
        """Handle /forget command."""
        count = int(args[0]) if args and args[0].isdigit() else 10
        
        deleted = short_memory.forget_last(user_id, count)
        
        await event.reply(f"🗑️ Forgot {deleted} recent messages.")
    
    async def _handle_forget_all(self, event, user_id: int):
        """Handle /forget_all command."""
        short_memory.forget_all(user_id)
        await event.reply("🗑️ Cleared all short-term memory.")
    
    async def _handle_wipe_me(self, event, user_id: int):
        """Handle /wipe_me command."""
        # Delete all user data
        db.delete_all_user_data(user_id)
        long_memory.delete_user_memories(user_id)
        file_processor.delete_user_files(user_id)
        
        await event.reply("🗑️ All your data has been permanently deleted.")
    
    async def _handle_export(self, event, user_id: int):
        """Handle /export command."""
        # Get user data
        stats = db.get_stats(user_id)
        facts = facts_store.get_facts(user_id)
        files = file_processor.get_user_files(user_id)
        
        # Build export data
        export_data = {
            "user_id": user_id,
            "export_date": datetime.now().isoformat(),
            "stats": stats,
            "facts": [{"key": f.key, "value": f.value, "confidence": f.confidence} 
                     for f in facts],
            "files": [{"name": f.name, "size": f.size, "uploaded": f.created_at.isoformat()} 
                     for f in files]
        }
        
        # Send as JSON
        import json
        export_text = json.dumps(export_data, indent=2, default=str)
        
        if len(export_text) > 4000:
            # Send as file if too large
            from io import BytesIO
            file_data = BytesIO(export_text.encode())
            file_data.name = f"export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            await event.reply(file=file_data)
        else:
            await event.reply(f"📊 Your data export:\n\n```json\n{export_text}\n```")
    
    async def _handle_mode(self, event, user_id: int, args: list):
        """Handle /mode command."""
        if not args:
            current_mode = facts_store.get_facts_dict(user_id).get("reply_mode", "default")
            await event.reply(f"Current mode: {current_mode}\n\nAvailable: concise, friendly, expert, bengali-first")
            return
        
        mode = args[0].lower()
        valid_modes = ["concise", "friendly", "expert", "bengali-first"]
        
        if mode in valid_modes:
            facts_store.add_fact(user_id, "reply_mode", mode)
            await event.reply(f"✅ Mode set to: {mode}")
        else:
            await event.reply(f"❌ Invalid mode. Use: {', '.join(valid_modes)}")
    
    async def _handle_stats(self, event, user_id: int):
        """Handle /stats command with professional analytics."""
        db_stats = db.get_stats(user_id)
        file_stats = file_processor.get_file_stats(user_id)
        short_stats = short_memory.get_stats(user_id)
        long_stats = long_memory.get_stats(user_id)
        
        response = """📊 **Analytics Dashboard**

**💬 Communication:**
• **Total Messages**: {messages}
• **Tokens Processed**: {tokens:,}

**📁 File Management:**
• **Files Uploaded**: {files}
• **Storage Used**: {storage} KB

**🧠 Memory Utilization:**
• **Short-term Memory**: {short_mem} messages
• **Long-term Memory**: {long_mem} memories
• **Personal Facts**: {facts} insights

**📈 Performance:**
• **Efficiency**: {efficiency}%
• **Data Density**: {density} KB/file""".format(
            messages=db_stats['message_count'],
            tokens=db_stats['total_tokens'],
            files=file_stats['file_count'],
            storage=file_stats['total_size'] // 1024,
            short_mem=short_stats['message_count'],
            long_mem=long_stats['message_memories'],
            facts=db_stats['fact_count'],
            efficiency=min(100, (db_stats['message_count'] * 100) // max(1, db_stats['total_tokens'] // 100)),
            density=max(1, file_stats['total_size'] // 1024) // max(1, file_stats['file_count'])
        )
        
        await event.reply(response)
    
    async def _handle_privacy(self, event):
        """Handle /privacy command with professional policy."""
        privacy_text = """🔒 **Privacy & Data Protection**

**Your Data, Your Control**

**📊 What We Store:**
• **Conversations** - Encrypted message history for context
• **Files** - Uploaded documents for AI processing
• **Preferences** - Your settings and personalization data

**🔐 Security Measures:**
• **Local Storage** - All data stays on your device
• **Encryption** - AES-256 encryption at rest
• **Zero Sharing** - No data sent to third parties

**⚡ Your Rights:**
• **Transparency** - `/export` to download everything
• **Deletion** - `/wipe_me` for complete data removal
• **Control** - `/forget` to manage memory

**🛡️ Data Retention:**
• **Automatic** - Deleted upon request
• **Secure** - Encrypted throughout lifecycle
• **Private** - Never shared or sold

**Questions?** Contact support or use `/help` for assistance."""
        
        await event.reply(privacy_text)
    
    async def _handle_admin(self, event):
        """Handle /admin command for owner."""
        # Get global stats
        from app.storage.db import db
        
        # This would need a method to get all users
        # For now, just show basic info
        await event.reply("👑 Admin Panel\n\nGlobal stats would be shown here.")