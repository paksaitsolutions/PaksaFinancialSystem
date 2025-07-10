"""
Logging configuration for the application.
"""
import logging
import logging.config
from pathlib import Path
from typing import Optional, Dict, Any

from ..core.config import settings

def setup_logging() -> None:
    """
    Configure logging for the application.
    
    Sets up console and file logging based on configuration.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                filename=logs_dir / "app.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8"
            )
        ]
    )
    
    # Set log level for specific loggers
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("uvicorn.access").handlers = logging.getLogger().handlers
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn").propagate = False
    logging.getLogger("uvicorn.access").propagate = False
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
