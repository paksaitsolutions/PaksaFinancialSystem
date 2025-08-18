"""
Logging configuration for the Paksa Financial System.

This module configures logging for the application with different log levels
for development and production environments.
"""
import logging
import logging.config
import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config import settings

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_JSON_FORMAT = """
{
    "timestamp": "%(asctime)s",
    "name": "%(name)s",
    "levelname": "%(levelname)s",
    "message": "%(message)s",
    "module": "%(module)s",
    "funcName": "%(funcName)s",
    "lineno": %(lineno)d,
    "process": %(process)d,
    "thread": %(thread)d
}
""".strip()

# Log file paths
ERROR_LOG_FILE = LOG_DIR / "error.log"
DEBUG_LOG_FILE = LOG_DIR / "debug.log"
ACCESS_LOG_FILE = LOG_DIR / "access.log"


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs JSON logs."""

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "levelname": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }

        # Add exception info if present
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        # Add any extra attributes
        if hasattr(record, "props") and isinstance(record.props, dict):
            log_record.update(record.props)

        return json.dumps(log_record, ensure_ascii=False)


def get_logger_config(env: str = "development") -> Dict[str, Any]:
    """Get the logging configuration based on the environment.

    Args:
        env: The environment (development, production, test)

    Returns:
        A dictionary with the logging configuration.
    """
    is_production = env.lower() == "production"
    is_test = env.lower() == "test"

    # Base configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": DEFAULT_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": f"{__name__}.JsonFormatter",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },
        "handlers": {},
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": True,
            },
            "app": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

    # Console handler (always enabled)
    config["handlers"]["console"] = {
        "class": "logging.StreamHandler",
        "formatter": "default",
        "stream": sys.stdout,
    }

    # Access log handler
    config["handlers"]["access"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "json" if is_production else "default",
        "filename": str(ACCESS_LOG_FILE),
        "maxBytes": 10485760,  # 10MB
        "backupCount": 5,
    }

    # File handler for errors
    config["handlers"]["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "json" if is_production else "default",
        "filename": str(ERROR_LOG_FILE),
        "maxBytes": 10485760,  # 10MB
        "backupCount": 5,
        "level": "ERROR",
    }

    # Debug file handler (only in development)
    if not is_production:
        config["handlers"]["debug_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": str(DEBUG_LOG_FILE),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "level": "DEBUG",
        }
        # Add debug file handler to app logger
        config["loggers"]["app"]["handlers"].append("debug_file")

    # In production, use JSON formatting and add file handlers
    if is_production:
        # Update console handler to use JSON in production
        config["handlers"]["console"]["formatter"] = "json"
        
        # Add file handler to root logger in production
        config["loggers"][""]["handlers"] = ["console", "file"]
        
        # Add file handler to app logger
        config["loggers"]["app"]["handlers"].append("file")
    
    # In test environment, make logs less verbose
    if is_test:
        config["loggers"]["app"]["level"] = "WARNING"
        config["loggers"]["sqlalchemy"]["level"] = "ERROR"

    return config


def setup_logging(env: Optional[str] = None) -> None:
    """Set up logging configuration.

    Args:
        env: The environment (development, production, test). If not provided,
            it will be read from the settings.
    """
    if env is None:
        env = settings.ENVIRONMENT

    # Get the logging configuration
    config = get_logger_config(env)

    # Apply the configuration
    logging.config.dictConfig(config)
    
    # Set up asyncio logging if needed
    if env != "test":
        logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Capture warnings from the warnings module
    logging.captureWarnings(True)
    
    # Set up SQLAlchemy logging
    if env == "development":
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class RequestIdFilter(logging.Filter):
    """Add request_id to log records."""
    
    def filter(self, record):
        from fastapi import Request
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.types import ASGIApp, Receive, Scope, Send
        
        request = getattr(record, "request", None)
        if request and hasattr(request, "state"):
            record.request_id = getattr(request.state, "request_id", "-")
        else:
            record.request_id = "-"
            
        return True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger with the given name.
    
    This is a convenience function that configures the logger if not already
    configured.
    
    Args:
        name: The name of the logger. If None, the root logger is returned.
        
    Returns:
        A configured logger instance.
    """
    if not logging.getLogger().handlers:
        setup_logging()
        
    logger = logging.getLogger(name)
    
    # Add request ID filter if not already added
    if not any(isinstance(f, RequestIdFilter) for f in logger.filters):
        logger.addFilter(RequestIdFilter())
        
    return logger
