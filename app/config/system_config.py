"""Easy system configuration management."""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SystemConfig:
    """Easy system configuration management with file-based updates."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize system configuration."""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.system_prompts_file = self.config_dir / "system_prompts.json"
        self.user_configs_file = self.config_dir / "user_configs.json"
        self.bot_settings_file = self.config_dir / "bot_settings.json"
        
        self.default_config = self._load_default_config()
        self.current_config = self._load_current_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "system_prompts": {},
            "bot_settings": {
                "max_response_length": 800,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "offline_mode": False,
                "reply_when_offline": False,
                "owner_commands": True,
                "auto_reply_enabled": True
            },
            "user_configs": {}
        }
    
    def _load_current_config(self) -> Dict[str, Any]:
        """Load current configuration from files."""
        config = self.default_config.copy()
        
        # Load system prompts
        if self.system_prompts_file.exists():
            try:
                with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                    config["system_prompts"].update(prompts)
            except Exception as e:
                logger.warning(f"Could not load system prompts: {e}")
        
        # Load user configs
        if self.user_configs_file.exists():
            try:
                with open(self.user_configs_file, 'r', encoding='utf-8') as f:
                    user_configs = json.load(f)
                    config["user_configs"].update(user_configs)
            except Exception as e:
                logger.warning(f"Could not load user configs: {e}")
        
        # Load bot settings
        if self.bot_settings_file.exists():
            try:
                with open(self.bot_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    config["bot_settings"].update(settings)
            except Exception as e:
                logger.warning(f"Could not load bot settings: {e}")
        
        return config
    
    def get_system_prompt(self, mode: str = "default") -> str:
        """Get system prompt for specified mode."""
        return self.current_config["system_prompts"].get(mode, self.current_config["system_prompts"]["default"])
    
    def update_system_prompt(self, mode: str, prompt: str):
        """Update system prompt for a mode."""
        self.current_config["system_prompts"][mode] = prompt
        self._save_system_prompts()
    
    def update_bot_setting(self, key: str, value: Any):
        """Update bot setting."""
        self.current_config["bot_settings"][key] = value
        self._save_bot_settings()
    
    def update_user_config(self, user_id: int, key: str, value: Any):
        """Update user-specific configuration."""
        if str(user_id) not in self.current_config["user_configs"]:
            self.current_config["user_configs"][str(user_id)] = {}
        self.current_config["user_configs"][str(user_id)][key] = value
        self._save_user_configs()
    
    def get_user_config(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get user-specific configuration."""
        user_str = str(user_id)
        if user_str in self.current_config["user_configs"]:
            return self.current_config["user_configs"][user_str].get(key, default)
        return default
    
    def get_bot_setting(self, key: str, default: Any = None) -> Any:
        """Get bot setting value."""
        return self.current_config["bot_settings"].get(key, default)
    
    def _save_system_prompts(self):
        """Save system prompts to file."""
        try:
            with open(self.system_prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_config["system_prompts"], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save system prompts: {e}")
    
    def _save_user_configs(self):
        """Save user configurations to file."""
        try:
            with open(self.user_configs_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_config["user_configs"], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save user configs: {e}")
    
    def _save_bot_settings(self):
        """Save bot settings to file."""
        try:
            with open(self.bot_settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_config["bot_settings"], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save bot settings: {e}")
    
    def reset_to_default(self):
        """Reset configuration to default."""
        self.current_config = self.default_config.copy()
        self._save_system_prompts()
        self._save_user_configs()
        self._save_bot_settings()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            "system_prompts_count": len(self.current_config["system_prompts"]),
            "user_configs_count": len(self.current_config["user_configs"]),
            "bot_settings": self.current_config["bot_settings"],
            "config_files": {
                "system_prompts": str(self.system_prompts_file),
                "user_configs": str(self.user_configs_file),
                "bot_settings": str(self.bot_settings_file)
            }
        }


# Global instance
system_config = SystemConfig()