"""
Audit logging middleware for automatic request tracking.
"""
import json
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.db.session import SessionLocal
from app.services.audit.audit_service import AuditService


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log API requests for audit purposes."""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs", "/redoc", "/openapi.json", "/health", "/metrics"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log audit information."""
        start_time = time.time()
        
        # Skip audit logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Extract request information
        method = request.method
        endpoint = request.url.path
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent")
        
        # Get user information if available
        user_id = None
        session_id = None
        
        try:
            # Try to extract user from request state (set by auth middleware)
            if hasattr(request.state, "user"):
                user_id = request.state.user.id
            
            if hasattr(request.state, "session_id"):
                session_id = request.state.session_id
        except:
            pass
        
        # Process request
        response = await call_next(request)
        
        # Log audit information for write operations or failed requests
        if self._should_log_request(method, response.status_code):
            try:
                await self._log_audit(
                    method=method,
                    endpoint=endpoint,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    user_id=user_id,
                    session_id=session_id,
                    status_code=response.status_code,
                    processing_time=time.time() - start_time
                )
            except Exception as e:
                # Don't let audit logging failures break the request
                print(f"Audit logging failed: {e}")
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _should_log_request(self, method: str, status_code: int) -> bool:
        """Determine if request should be logged."""
        # Always log write operations
        if method in ["POST", "PUT", "PATCH", "DELETE"]:
            return True
        
        # Log failed requests
        if status_code >= 400:
            return True
        
        # Skip GET requests for now (can be configured)
        return False
    
    async def _log_audit(
        self,
        method: str,
        endpoint: str,
        ip_address: str,
        user_agent: str,
        user_id: str = None,
        session_id: str = None,
        status_code: int = None,
        processing_time: float = None
    ):
        """Log audit information to database."""
        db = SessionLocal()
        try:
            audit_service = AuditService(db)
            
            # Determine action based on method and endpoint
            action = self._determine_action(method, endpoint)
            resource_type = self._determine_resource_type(endpoint)
            
            # Create metadata
            metadata = {
                "status_code": status_code,
                "processing_time": processing_time
            }
            
            # Log the audit entry
            audit_service.log_action(
                action=action,
                resource_type=resource_type,
                user_id=user_id,
                session_id=session_id,
                endpoint=endpoint,
                method=method,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata,
                description=f"{method} {endpoint} - Status: {status_code}"
            )
        finally:
            db.close()
    
    def _determine_action(self, method: str, endpoint: str) -> str:
        """Determine audit action based on HTTP method and endpoint."""
        if method == "POST":
            if "login" in endpoint.lower():
                return "login"
            elif "logout" in endpoint.lower():
                return "logout"
            else:
                return "create"
        elif method == "GET":
            return "read"
        elif method in ["PUT", "PATCH"]:
            return "update"
        elif method == "DELETE":
            return "delete"
        else:
            return method.lower()
    
    def _determine_resource_type(self, endpoint: str) -> str:
        """Determine resource type from endpoint."""
        # Extract resource type from endpoint path
        path_parts = endpoint.strip("/").split("/")
        
        # Skip API version prefix
        if path_parts and path_parts[0].startswith("v"):
            path_parts = path_parts[1:]
        
        # Return the first meaningful path segment
        if path_parts:
            return path_parts[0]
        
        return "unknown"