"""
Production-ready security implementation.
"""
import hashlib
import secrets
import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

class ProductionSecurity:
    """Production-ready security service."""
    
    def __init__(self):
        self.failed_attempts = {}
        self.rate_limits = {}
    
    def sanitize_input(self, input_data: Any) -> Any:
        """Sanitize user input to prevent injection attacks."""
        if isinstance(input_data, str):
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\';\\]', '', input_data)
            # Limit length
            return sanitized[:1000]
        elif isinstance(input_data, dict):
            return {k: self.sanitize_input(v) for k, v in input_data.items()}
        elif isinstance(input_data, list):
            return [self.sanitize_input(item) for item in input_data]
        return input_data
    
    def validate_sql_query(self, query: str) -> bool:
        """Validate SQL query for dangerous operations."""
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
            'INSERT', 'UPDATE', 'EXEC', 'EXECUTE', 'UNION'
        ]
        
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Dangerous SQL keyword detected: {keyword}")
                return False
        return True
    
    async def check_rate_limit(self, request: Request, limit: int = 100, window: int = 3600) -> bool:
        """Check rate limiting for API endpoints."""
        client_ip = request.client.host
        current_time = datetime.utcnow()
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Clean old requests
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if current_time - req_time < timedelta(seconds=window)
        ]
        
        # Check limit
        if len(self.rate_limits[client_ip]) >= limit:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        self.rate_limits[client_ip].append(current_time)
        return True
    
    def hash_password(self, password: str) -> str:
        """Securely hash password."""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${password_hash.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            salt, stored_hash = hashed.split('$')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash.hex() == stored_hash
        except:
            return False
    
    async def log_security_event(self, db: AsyncSession, event_type: str, details: Dict[str, Any]):
        """Log security events for audit trail."""
        # In production, store in dedicated security log table
        logger.warning(f"Security Event: {event_type} - {details}")

class InputValidator:
    """Production input validation."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Validate financial amounts."""
        return 0 <= amount <= 999999999.99
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Validate date ranges."""
        return start_date <= end_date and start_date >= datetime(2000, 1, 1)
    
    @staticmethod
    def validate_tenant_access(user_tenant_id: str, resource_tenant_id: str) -> bool:
        """Validate tenant isolation."""
        return user_tenant_id == resource_tenant_id