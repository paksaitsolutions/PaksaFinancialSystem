"""CSRF protection middleware"""
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
import secrets
import hmac
import hashlib

class CSRFProtection:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        nonce = secrets.token_urlsafe(32)
        message = f"{session_id}:{nonce}"
        signature = hmac.new(self.secret_key, message.encode(), hashlib.sha256).hexdigest()
        return f"{nonce}:{signature}"
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        try:
            nonce, signature = token.split(':', 1)
            message = f"{session_id}:{nonce}"
            expected = hmac.new(self.secret_key, message.encode(), hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected)
        except:
            return False

csrf_protection = CSRFProtection("your-secret-key")

async def csrf_middleware(request: Request, call_next):
    """CSRF middleware for state-changing requests"""
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        csrf_token = request.headers.get("X-CSRF-Token")
        session_id = request.headers.get("X-Session-ID", "")
        
        if not csrf_token or not csrf_protection.validate_token(csrf_token, session_id):
            raise HTTPException(status_code=403, detail="CSRF token invalid")
    
    response = await call_next(request)
    return response