from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import hashlib
from ..core.security import RateLimiter
from ..core.config import settings

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Security headers
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    
                    # Add security headers
                    security_headers = {
                        b"x-content-type-options": b"nosniff",
                        b"x-frame-options": b"DENY",
                        b"x-xss-protection": b"1; mode=block",
                        b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                        b"content-security-policy": b"default-src 'self'",
                        b"referrer-policy": b"strict-origin-when-cross-origin",
                        b"permissions-policy": b"geolocation=(), microphone=(), camera=()"
                    }
                    
                    for key, value in security_headers.items():
                        headers[key] = value
                    
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            # Rate limiting check
            try:
                client_ip = request.client.host
                RateLimiter.check_rate_limit(request, client_ip)
            except HTTPException as e:
                response = JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )
                await response(scope, receive, send)
                return
            
            # Request validation
            if not self.validate_request(request):
                response = JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request"}
                )
                await response(scope, receive, send)
                return
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
    
    def validate_request(self, request: Request) -> bool:
        """Validate request for security threats"""
        
        # Check for SQL injection patterns
        dangerous_patterns = [
            "union select", "drop table", "delete from", 
            "insert into", "update set", "--", "/*", "*/"
        ]
        
        query_string = str(request.url.query).lower()
        for pattern in dangerous_patterns:
            if pattern in query_string:
                return False
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            return False
        
        # Check for suspicious headers
        user_agent = request.headers.get("user-agent", "").lower()
        if not user_agent or "bot" in user_agent or "crawler" in user_agent:
            # Allow legitimate bots but log suspicious activity
            pass
        
        return True

class CSRFMiddleware:
    def __init__(self, app):
        self.app = app
        self.exempt_paths = ["/auth/login", "/auth/register", "/docs", "/openapi.json"]

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip CSRF for exempt paths and GET requests
            if (request.url.path in self.exempt_paths or 
                request.method in ["GET", "HEAD", "OPTIONS"]):
                await self.app(scope, receive, send)
                return
            
            # Validate CSRF token
            csrf_token = request.headers.get("x-csrf-token")
            if not csrf_token or not self.validate_csrf_token(csrf_token, request):
                response = JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF token missing or invalid"}
                )
                await response(scope, receive, send)
                return
            
            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)
    
    def validate_csrf_token(self, token: str, request: Request) -> bool:
        """Validate CSRF token"""
        # Simple CSRF validation - implement proper token validation
        expected_token = self.generate_csrf_token(request)
        return token == expected_token
    
    def generate_csrf_token(self, request: Request) -> str:
        """Generate CSRF token"""
        # Simple implementation - use proper CSRF token generation in production
        session_id = request.headers.get("x-session-id", "default")
        return hashlib.sha256(f"{session_id}{settings.SECRET_KEY}".encode()).hexdigest()[:32]