"""
Tenant context middleware for multi-tenant request handling.
"""
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

from app.core.logging import logger

class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate tenant context from requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with tenant context."""
        
        # Skip tenant validation for auth and health endpoints
        skip_paths = ['/auth/', '/health', '/docs', '/openapi.json']
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Extract tenant ID from various sources
        tenant_id = self._extract_tenant_id(request)
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant ID is required"
            )
        
        # Validate tenant ID format
        try:
            uuid.UUID(tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tenant ID format"
            )
        
        # Set tenant context in request state
        request.state.tenant_id = tenant_id
        
        # Add tenant ID to response headers for debugging
        response = await call_next(request)
        response.headers["X-Tenant-ID"] = tenant_id
        
        return response
    
    def _extract_tenant_id(self, request: Request) -> str:
        """Extract tenant ID from request headers, query params, or JWT token."""
        
        # 1. Check X-Tenant-ID header
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            return tenant_id
        
        # 2. Check query parameter
        tenant_id = request.query_params.get("tenant_id")
        if tenant_id:
            return tenant_id
        
        # 3. Extract from JWT token (if available)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            tenant_id = self._extract_tenant_from_jwt(token)
            if tenant_id:
                return tenant_id
        
        return None
    
    def _extract_tenant_from_jwt(self, token: str) -> str:
        """Extract tenant ID from JWT token payload."""
        try:
            import jwt
            from app.core.config import settings
            
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"],
                options={"verify_exp": False}  # Skip expiration for tenant extraction
            )
            return payload.get("tenant_id")
            
        except Exception as e:
            logger.warning(f"Failed to extract tenant from JWT: {str(e)}")
            return None

def get_current_tenant_id(request: Request) -> str:
    """Get current tenant ID from request state."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context not found"
        )
    return tenant_id