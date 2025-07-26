"""
Production error handling and logging.
"""
import traceback
import logging
from typing import Any, Dict
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)

class ProductionErrorHandler:
    """Production-ready error handling."""
    
    @staticmethod
    async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle database errors."""
        error_id = f"DB_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.error(f"Database Error [{error_id}]: {str(exc)}")
        
        if isinstance(exc, IntegrityError):
            user_message = "Data integrity constraint violated."
            status_code = 400
        else:
            user_message = "Database operation failed."
            status_code = 500
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": True,
                "message": user_message,
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions."""
        error_id = f"GEN_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.error(f"Unhandled Error [{error_id}]: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "An unexpected error occurred.",
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class AuditLogger:
    """Production audit logging."""
    
    def log_user_action(self, user_id: str, tenant_id: str, action: str, resource: str):
        """Log user actions for audit trail."""
        logger.info(f"AUDIT: User {user_id} performed {action} on {resource}")
    
    def log_data_change(self, user_id: str, table: str, record_id: str, changes: Dict[str, Any]):
        """Log data changes for compliance."""
        logger.info(f"DATA_CHANGE: User {user_id} modified {table}:{record_id}")
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events."""
        logger.warning(f"SECURITY: {event_type} - {details}")

audit_logger = AuditLogger()