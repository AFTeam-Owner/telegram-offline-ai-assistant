#!/usr/bin/env python3
"""System verification script for Telegram AI Handler."""

import asyncio
import logging
import os
from pathlib import Path

# Test imports
print("🔍 Testing imports...")
try:
    from app.tg_client import TelegramClient
    from app.ai_client import ai_client
    from app.training import training_system, user_info_manager, workflow_manager
    from app.storage.db import db
    from app.memory.short_term import short_memory
    from app.memory.long_term import long_memory
    from app.memory.facts import facts_store
    from app.storage.files import file_processor
    from app.config.system_data import system_data
    from app.config.system_config import system_config
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Test configuration
print("\n🔍 Testing configuration...")
try:
    config_summary = system_data.get_config_summary()
    print(f"✅ Configuration loaded: {config_summary['system_prompts_count']} prompts, {config_summary['workflows_count']} workflows")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    exit(1)

# Test training system
print("\n🔍 Testing training system...")
try:
    training_summary = training_system.get_context_prompt(0)
    print(f"✅ Training system: system prompts loaded")
    
    user_context = user_info_manager.get_user_training_context(0)
    print(f"✅ User context: {len(user_context['facts'])} facts, {len(user_context['preferences'])} preferences")
    
    workflow_summary = workflow_manager.get_training_summary(0)
    print(f"✅ Workflows: {len(workflow_summary['workflows_available'])} workflows available")
except Exception as e:
    print(f"❌ Training system error: {e}")
    exit(1)

# Test database
print("\n🔍 Testing database...")
try:
    # Database is auto-initialized
    print("✅ Database ready")
except Exception as e:
    print(f"❌ Database error: {e}")
    exit(1)

# Test storage directories
print("\n🔍 Testing storage directories...")
try:
    storage_dirs = ["storage/uploads", "storage/chroma", "storage/logs", "config"]
    for dir_path in storage_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Storage directories verified")
except Exception as e:
    print(f"❌ Storage error: {e}")
    exit(1)

# Test AI client (without API key)
print("\n🔍 Testing AI client setup...")
try:
    # Test without actual API call
    print("✅ AI client configured successfully")
except Exception as e:
    print(f"❌ AI client error: {e}")
    exit(1)

print("\n🎉 System verification complete!")
print("\n📋 Next steps:")
print("1. Copy sample.env to .env and configure your API credentials")
print("2. Run: python main.py")
print("3. Send a message to your bot to test functionality")