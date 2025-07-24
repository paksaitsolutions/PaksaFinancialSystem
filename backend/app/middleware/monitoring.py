"""
Monitoring middleware.
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import log_request, log_response, log_error
from app.core.monitoring import metrics

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for request monitoring and logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with monitoring."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract tenant and user info
        tenant_id = request.headers.get("X-Tenant-ID")
        user_id = request.headers.get("X-User-ID")
        
        # Log request
        log_request(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        # Record metrics
        metrics.record_request(request.method, request.url.path, tenant_id)
        
        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record response metrics
            metrics.record_response_time(request.method, request.url.path, duration)
            
            # Log response
            log_response(request_id, response.status_code, duration)
            
            # Add monitoring headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error metrics
            metrics.record_error(type(e).__name__, tenant_id)
            
            # Log error
            log_error(e, request_id, tenant_id)
            
            raise