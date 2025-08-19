"""Professional UI formatting utilities for Telegram bot responses."""

import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class UIFormatter:
    """Professional UI formatting for Telegram bot responses."""
    
    @staticmethod
    def format_header(title: str, emoji: str = "📊") -> str:
        """Format a professional header."""
        return f"{emoji} **{title.upper()}**"
    
    @staticmethod
    def format_section(title: str, content: str, emoji: str = "•") -> str:
        """Format a professional section."""
        return f"\n**{title}:**\n{content}"
    
    @staticmethod
    def format_bullet_list(items: List[str], emoji: str = "•") -> str:
        """Format a professional bullet list."""
        return "\n".join(f"{emoji} {item}" for item in items)
    
    @staticmethod
    def format_key_value(key: str, value: Any, emoji: str = "→") -> str:
        """Format key-value pairs professionally."""
        return f"{emoji} **{key}:** {value}"
    
    @staticmethod
    def format_success(message: str) -> str:
        """Format success messages."""
        return f"✅ **Success:** {message}"
    
    @staticmethod
    def format_error(message: str) -> str:
        """Format error messages."""
        return f"❌ **Error:** {message}"
    
    @staticmethod
    def format_warning(message: str) -> str:
        """Format warning messages."""
        return f"⚠️ **Warning:** {message}"
    
    @staticmethod
    def format_info(message: str) -> str:
        """Format info messages."""
        return f"ℹ️ **Info:** {message}"
    
    @staticmethod
    def format_timestamp() -> str:
        """Format current timestamp professionally."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """Format file size professionally."""
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size // 1024} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size // (1024 * 1024)} MB"
        else:
            return f"{bytes_size // (1024 * 1024 * 1024)} GB"

    @staticmethod
    def format_status_card(title: str, data: Dict[str, Any]) -> str:
        """Format a professional status card."""
        lines = [f"📊 **{title}**"]
        lines.append("─" * 30)
        for key, value in data.items():
            lines.append(f"**{key}:** `{value}`")
        return "\n".join(lines)

    @staticmethod
    def format_command_help() -> str:
        """Format command help professionally."""
        return """🤖 **Bot Commands**

**Owner Commands:**
`/config start` - Enable auto-reply
`/config stop` - Disable auto-reply
`/config status` - Check current status
`/config reload` - Reload configuration
`/config reset` - Reset to defaults

**General Commands:**
`/help` - Show this help message"""
    
    @staticmethod
    def format_welcome_message() -> str:
        """Format welcome message professionally."""
        return """🤖 **Welcome to Telegram Offline AI Assistant!**

I'm your intelligent assistant that responds only when you're offline.

**Features:**
• **Context-aware conversations**
• **Memory management**
• **Professional formatting**
• **Owner control commands**

**Commands:**
• `/config start` - Enable replies
• `/config stop` - Disable replies
• `/config status` - Check status

Ready to assist you!"""
    
    @staticmethod
    def format_status_report(enabled: bool, config: Dict[str, Any]) -> str:
        """Format a comprehensive status report."""
        status = "🟢 **ONLINE**" if enabled else "🔴 **OFFLINE**"
        
        lines = [
            "📊 **System Status Report**",
            "─" * 30,
            f"**Status:** {status}",
            f"**Max Response Length:** {config.get('max_response_length', 800)}",
            f"**Temperature:** {config.get('temperature', 0.7)}",
            f"**Top P:** {config.get('top_p', 0.9)}",
            "",
            "✅ **System Ready**"
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def format_config_updated(action: str, details: str = "") -> str:
        """Format configuration update messages."""
        return f"✅ **Configuration Updated**\n\n**Action:** {action}\n{details}"
    
    @staticmethod
    def format_error_with_details(error: str, details: str = "") -> str:
        """Format error messages with details."""
        message = f"❌ **Error:** {error}"
        if details:
            message += f"\n\n**Details:** {details}"
        return message


# Global formatter instance
ui_formatter = UIFormatter()