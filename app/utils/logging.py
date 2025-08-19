"""Logging configuration for the application."""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from app.utils.tokens import sanitize_for_logging


class SensitiveDataFilter(logging.Filter):
    """Filter to remove sensitive data from logs."""
    
    def filter(self, record):
        if hasattr(record, 'msg'):
            record.msg = sanitize_for_logging(str(record.msg))
        if hasattr(record, 'args'):
            record.args = tuple(sanitize_for_logging(str(arg)) if isinstance(arg, str) else arg 
                              for arg in record.args)
        return True


def setup_logging(level: str = "INFO") -> None:
    """Setup application logging with appropriate format and handlers."""
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logs directory
    log_dir = Path("storage/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                log_dir / f"telegram_handler_{datetime.now().strftime('%Y%m%d')}.log"
            )
        ]
    )
    
    # Add sensitive data filter to all handlers
    for handler in logging.root.handlers:
        handler.addFilter(SensitiveDataFilter())
    
    # Set specific log levels for external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)