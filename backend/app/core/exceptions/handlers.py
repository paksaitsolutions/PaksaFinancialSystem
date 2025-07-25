"""Standardized exception handling"""
from fastapi import HTTPException
from app.core.logging.config import get_logger
import traceback

logger = get_logger("exceptions")

class BaseAppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ValidationError(BaseAppException):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")

class NotFoundError(BaseAppException):
    """Resource not found error"""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", "NOT_FOUND")

def handle_exception(func):
    """Decorator for standardized exception handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseAppException as e:
            logger.error(f"Application error in {func.__name__}: {e.message}")
            raise HTTPException(status_code=400, detail={"error": {"code": e.code, "message": e.message}})
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}})
    return wrapper