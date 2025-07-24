"""
Authentication middleware for permission validation.
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional

security = HTTPBearer(auto_error=False)

class AuthMiddleware:
    """Authentication middleware."""
    
    def __init__(self, secret_key: str = "your-secret-key"):
        self.secret_key = secret_key
    
    async def __call__(self, request: Request, call_next):
        """Process request with authentication."""
        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Extract token
        token = self._extract_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Validate token and set user context
        try:
            user_data = self._decode_token(token)
            request.state.user = user_data
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return await call_next(request)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public."""
        public_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/auth/login"
        ]
        return any(path.startswith(p) for p in public_paths)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract token from request."""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None
    
    def _decode_token(self, token: str) -> dict:
        """Decode JWT token."""
        # Mock implementation - in real app, decode actual JWT
        return {
            "user_id": "mock-user-id",
            "role": "admin",
            "permissions": ["inventory:read", "inventory:write", "tax:read", "tax:write", "ar:read"]
        }