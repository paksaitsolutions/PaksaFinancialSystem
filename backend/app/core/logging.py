"""
Application logging configuration.
"""
import logging
import sys
from typing import Dict, Any
from datetime import datetime
import json

from app.core.config import settings

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, 'tenant_id'):
            log_entry['tenant_id'] = record.tenant_id
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        
        # Add exception info
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging():
    """Setup application logging."""
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)
    
    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # Application logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    # Database logger
    db_logger = logging.getLogger("sqlalchemy.engine")
    db_logger.setLevel(logging.WARNING if not settings.DEBUG else logging.INFO)
    
    return app_logger

# Global logger instance
logger = setup_logging()

def log_request(request_id: str, method: str, path: str, tenant_id: str = None, user_id: str = None):
    """Log HTTP request."""
    logger.info(
        f"Request {method} {path}",
        extra={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "method": method,
            "path": path
        }
    )

def log_response(request_id: str, status_code: int, duration: float):
    """Log HTTP response."""
    logger.info(
        f"Response {status_code}",
        extra={
            "request_id": request_id,
            "status_code": status_code,
            "duration": duration
        }
    )

def log_error(error: Exception, request_id: str = None, tenant_id: str = None):
    """Log application error."""
    logger.error(
        f"Error: {str(error)}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "error_type": type(error).__name__
        }
    )