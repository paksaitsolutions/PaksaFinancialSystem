"""Security audit logging"""
from app.core.logging.config import get_logger
from datetime import datetime
from typing import Optional

logger = get_logger("security_audit")

class SecurityAuditLogger:
    @staticmethod
    def log_login_attempt(user_id: Optional[str], ip_address: str, success: bool, tenant_id: Optional[str] = None):
        """Log login attempt"""
        logger.info("Login attempt", extra={
            "event_type": "login_attempt",
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @staticmethod
    def log_permission_denied(user_id: str, resource: str, action: str, tenant_id: Optional[str] = None):
        """Log permission denied"""
        logger.warning("Permission denied", extra={
            "event_type": "permission_denied",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @staticmethod
    def log_data_access(user_id: str, resource: str, action: str, record_id: Optional[str] = None, tenant_id: Optional[str] = None):
        """Log data access"""
        logger.info("Data access", extra={
            "event_type": "data_access",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "record_id": record_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @staticmethod
    def log_security_violation(violation_type: str, details: dict, ip_address: str, user_id: Optional[str] = None):
        """Log security violation"""
        logger.error("Security violation", extra={
            "event_type": "security_violation",
            "violation_type": violation_type,
            "details": details,
            "ip_address": ip_address,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })

audit_logger = SecurityAuditLogger()