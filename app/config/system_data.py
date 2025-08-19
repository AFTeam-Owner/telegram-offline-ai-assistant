"""Easy system data management with file-based configuration."""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SystemDataManager:
    """Easy system data management with file-based updates."""
    
    def __init__(self, data_dir: str = "config"):
        """Initialize system data manager."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.system_data_file = self.data_dir / "system_data.json"
        self.prompts_file = self.data_dir / "prompts.json"
        self.workflows_file = self.data_dir / "workflows.json"
        
        self.default_data = self._load_default_data()
        self.current_data = self._load_current_data()
    
    def _load_default_data(self) -> Dict[str, Any]:
        """Load default system data."""
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
                "easy_config_update": True
            },
            "workflows": {},
            "training_data": {}
        }
    
    def _load_current_data(self) -> Dict[str, Any]:
        """Load current system data from files."""
        data = self.default_data.copy()
        
        # Load system prompts
        if self.prompts_file.exists():
            try:
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                    data["system_prompts"].update(prompts)
            except Exception as e:
                logger.warning(f"Could not load system prompts: {e}")
        
        # Load workflows
        if self.workflows_file.exists():
            try:
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    workflows = json.load(f)
                    data["workflows"].update(workflows)
            except Exception as e:
                logger.warning(f"Could not load workflows: {e}")
        
        # Load training data
        if self.system_data_file.exists():
            try:
                with open(self.system_data_file, 'r', encoding='utf-8') as f:
                    system_data = json.load(f)
                    data.update(system_data)
            except Exception as e:
                logger.warning(f"Could not load system data: {e}")
        
        return data
    
    def get_system_prompt(self, mode: str = "default") -> str:
        """Get system prompt for specified mode."""
        return self.current_data["system_prompts"].get(mode, "You are a helpful AI assistant.")
    
    def update_system_prompt(self, mode: str, prompt: str):
        """Update system prompt for a mode."""
        self.current_data["system_prompts"][mode] = prompt
        self._save_data()
    
    def update_bot_setting(self, key: str, value: Any):
        """Update bot setting."""
        self.current_data["bot_settings"][key] = value
        self._save_data()
    
    def update_workflow(self, name: str, workflow: Dict[str, Any]):
        """Update workflow."""
        self.current_data["workflows"][name] = workflow
        self._save_data()
    
    def update_training_data(self, category: str, data: List[Dict[str, Any]]):
        """Update training data."""
        self.current_data["training_data"][category] = data
        self._save_data()
    
    def load_from_txt_file(self, file_path: str) -> bool:
        """Load configuration from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse simple key-value format
            lines = content.strip().split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key.startswith("prompt_"):
                        mode = key.replace("prompt_", "")
                        self.update_system_prompt(mode, value)
                    elif key.startswith("setting_"):
                        setting = key.replace("setting_", "")
                        self.update_bot_setting(setting, value)
                    elif key.startswith("workflow_"):
                        workflow = key.replace("workflow_", "")
                        self.update_workflow(workflow, {"name": workflow, "response": value})
            
            return True
        except Exception as e:
            logger.error(f"Could not load from txt file: {e}")
            return False
    
    def save_to_txt_file(self, file_path: str) -> bool:
        """Save configuration to a text file."""
        try:
            content = []
            content.append("# System Prompts")
            for mode, prompt in self.current_data["system_prompts"].items():
                content.append(f"prompt_{mode}={prompt}")
            
            content.append("\n# Bot Settings")
            for key, value in self.current_data["bot_settings"].items():
                content.append(f"setting_{key}={value}")
            
            content.append("\n# Workflows")
            for name, workflow in self.current_data["workflows"].items():
                content.append(f"workflow_{name}={workflow.get('response_template', '')}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            return True
        except Exception as e:
            logger.error(f"Could not save to txt file: {e}")
            return False
    
    def reset_to_default(self):
        """Reset configuration to default."""
        self.current_data = self.default_data.copy()
        self._save_data()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            "system_prompts_count": len(self.current_data["system_prompts"]),
            "workflows_count": len(self.current_data["workflows"]),
            "training_data_count": len(self.current_data["training_data"]),
            "bot_settings": self.current_data["bot_settings"],
            "config_files": {
                "system_data": str(self.system_data_file),
                "prompts": str(self.prompts_file),
                "workflows": str(self.workflows_file)
            }
        }
    
    def _save_data(self):
        """Save all data to files."""
        try:
            # Save system data
            with open(self.system_data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "bot_settings": self.current_data["bot_settings"],
                    "training_data": self.current_data["training_data"]
                }, f, indent=2, ensure_ascii=False)
            
            # Save prompts
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data["system_prompts"], f, indent=2, ensure_ascii=False)
            
            # Save workflows
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data["workflows"], f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Could not save data: {e}")
    
    def get_training_data(self, category: str) -> list:
        """Get training data for a category."""
        return self.current_data["training_data"].get(category, [])
    
    def add_training_example(self, category: str, user_input: str, bot_response: str):
        """Add training example."""
        if category not in self.current_data["training_data"]:
            self.current_data["training_data"][category] = []
        
        self.current_data["training_data"][category].append({
            "user": user_input,
            "bot": bot_response
        })
        self._save_data()


# Global instance
system_data = SystemDataManager()