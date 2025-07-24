from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from app.core.config import settings

class TenantContext:
    def __init__(self):
        self.tenant_id: Optional[str] = None
        self.company_id: Optional[int] = None

tenant_context = TenantContext()

def get_tenant_from_request(request: Request) -> str:
    """Extract tenant_id from request headers or JWT token"""
    
    # Try to get tenant from header
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        return tenant_id
    
    # Try to get from subdomain
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        if subdomain not in ["www", "api"]:
            return subdomain
    
    # Try to get from JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload.get("tenant_id")
        except jwt.InvalidTokenError:
            pass
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Tenant ID not found in request"
    )

def set_tenant_context(tenant_id: str, company_id: int = None):
    """Set the current tenant context"""
    tenant_context.tenant_id = tenant_id
    tenant_context.company_id = company_id

def get_current_tenant() -> str:
    """Get current tenant ID"""
    if not tenant_context.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context set"
        )
    return tenant_context.tenant_id

def clear_tenant_context():
    """Clear tenant context"""
    tenant_context.tenant_id = None
    tenant_context.company_id = None