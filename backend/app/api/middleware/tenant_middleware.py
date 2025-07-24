from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from app.core.db.tenant_middleware import get_tenant_from_request, set_tenant_context, clear_tenant_context
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/api/v1/auth/login"]
        
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        try:
            tenant_id = get_tenant_from_request(request)
            set_tenant_context(tenant_id)
            
            response = await call_next(request)
            response.headers["X-Tenant-ID"] = tenant_id
            
            return response
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Tenant middleware error: {e}")
            raise HTTPException(status_code=500, detail="Tenant processing error")
        finally:
            clear_tenant_context()