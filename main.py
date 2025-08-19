#!/usr/bin/env python3
"""
Telegram AI Handler - Main Entry Point
"""
import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from app.tg_client import TelegramClient
from app.utils.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
ENV = os.getenv("ENV", "dev")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENV == "prod" else "DEBUG")
setup_logging(LOG_LEVEL)

logger = logging.getLogger(__name__)


async def main():
    """Main application entry point."""
    logger.info("Starting Telegram AI Handler...")
    
    # Ensure storage directories exist
    storage_dirs = ["storage/uploads", "storage/chroma", "storage/logs"]
    for dir_path in storage_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Initialize and start Telegram client
    tg_client = TelegramClient()
    await tg_client.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise