from typing import Any, Optional
from pydantic import BaseModel, validator, Field
import re
import html
from sqlalchemy import text

class SecureBaseModel(BaseModel):
    """Base model with security validations"""
    
    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            # HTML escape to prevent XSS
            v = html.escape(v.strip())
            # Remove potential SQL injection patterns
            dangerous_patterns = [';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC']
            for pattern in dangerous_patterns:
                if pattern.upper() in v.upper():
                    raise ValueError(f"Invalid input: contains dangerous pattern")
        return v

class AccountCodeValidator:
    @staticmethod
    def validate(code: str) -> str:
        if not code or not isinstance(code, str):
            raise ValueError("Account code is required")
        
        code = code.strip()
        if not re.match(r'^[A-Z0-9-]{1,20}$', code):
            raise ValueError("Account code must be alphanumeric with dashes, max 20 chars")
        
        return code

class EmailValidator:
    @staticmethod
    def validate(email: str) -> str:
        if not email or not isinstance(email, str):
            raise ValueError("Email is required")
        
        email = email.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        
        return email

class TenantIdValidator:
    @staticmethod
    def validate(tenant_id: str) -> str:
        if not tenant_id or not isinstance(tenant_id, str):
            raise ValueError("Tenant ID is required")
        
        tenant_id = tenant_id.strip()
        if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', tenant_id):
            raise ValueError("Invalid tenant ID format")
        
        return tenant_id

def sanitize_sql_input(value: Any) -> Any:
    """Sanitize input for SQL queries"""
    if isinstance(value, str):
        # Remove dangerous SQL patterns
        value = re.sub(r'[;\'\"\\]', '', value)
        value = re.sub(r'--.*$', '', value, flags=re.MULTILINE)
        value = re.sub(r'/\*.*?\*/', '', value, flags=re.DOTALL)
    return value