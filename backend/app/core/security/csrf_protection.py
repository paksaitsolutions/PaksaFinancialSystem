from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
import secrets
import hmac
import hashlib
from typing import Optional
import time

class CSRFProtection:
    def __init__(self, secret_key: str, token_lifetime: int = 3600):
        self.secret_key = secret_key.encode()
        self.token_lifetime = token_lifetime
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        signature = hmac.new(
            self.secret_key,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{timestamp}:{signature}"
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        try:
            timestamp_str, signature = token.split(':', 1)
            timestamp = int(timestamp_str)
            
            # Check token age
            if time.time() - timestamp > self.token_lifetime:
                return False
            
            # Verify signature
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                self.secret_key,
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, IndexError):
            return False

csrf_protection = CSRFProtection("your-secret-key")

async def verify_csrf_token(request: Request):
    """Middleware to verify CSRF token"""
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        csrf_token = request.headers.get("X-CSRF-Token")
        session_id = request.headers.get("X-Session-ID", "")
        
        if not csrf_token or not csrf_protection.validate_token(csrf_token, session_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )