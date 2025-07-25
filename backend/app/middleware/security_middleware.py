from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from app.core.security.csrf_protection import verify_csrf_token
from app.core.security.rate_limiter import tenant_rate_limiter
from app.core.security.input_validation import sanitize_sql_input
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip security checks for health endpoints
        if request.url.path in ["/health", "/docs", "/redoc"]:
            return await call_next(request)
        
        try:
            # 1. CSRF Protection
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                await verify_csrf_token(request)
            
            # 2. Rate Limiting
            await self._check_rate_limits(request)
            
            # 3. Input Sanitization
            await self._sanitize_request_data(request)
            
            # 4. Security Headers
            response = await call_next(request)
            self._add_security_headers(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            raise
    
    async def _check_rate_limits(self, request: Request):
        """Check rate limits for the request"""
        from app.core.db.tenant_middleware import get_current_tenant
        from fastapi import HTTPException, status
        
        try:
            tenant_id = get_current_tenant()
            limit_type = self._get_limit_type(request.url.path)
            key = tenant_rate_limiter.get_tenant_key(request, tenant_id, limit_type)
            
            if not tenant_rate_limiter.check_rate_limit(key, limit_type):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
        except Exception:
            # Fallback to IP-based limiting if tenant context fails
            pass
    
    async def _sanitize_request_data(self, request: Request):
        """Sanitize request data to prevent injection attacks"""
        # This is a simplified approach - in production, you'd want more sophisticated sanitization
        if hasattr(request, 'json'):
            try:
                body = await request.json()
                if isinstance(body, dict):
                    for key, value in body.items():
                        if isinstance(value, str):
                            body[key] = sanitize_sql_input(value)
            except:
                pass  # Not JSON data
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    def _get_limit_type(self, path: str) -> str:
        """Determine rate limit type based on path"""
        if "/auth/login" in path:
            return "login"
        elif "/upload" in path:
            return "upload"
        else:
            return "api"