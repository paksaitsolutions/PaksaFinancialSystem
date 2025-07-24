"""
Multi-tenant authentication API endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.tenant_auth_schemas import (
    TenantAuthConfigRequest,
    TenantAuthConfigResponse,
    TenantLoginRequest,
    TenantLoginResponse,
    TenantSessionResponse,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    OAuthProviderRequest,
    OAuthProviderResponse,
    CompanySelectionResponse,
    LoginAttemptResponse
)
from app.services.auth.tenant_auth_service import TenantAuthService

router = APIRouter()


def get_tenant_auth_service(db: Session = Depends(get_db)) -> TenantAuthService:
    """Get tenant auth service instance."""
    return TenantAuthService(db)


@router.post(
    "/config/{company_id}",
    response_model=TenantAuthConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create auth config",
    description="Create authentication configuration for a company.",
    tags=["Tenant Auth Config"]
)
async def create_auth_config(
    company_id: UUID,
    config_request: TenantAuthConfigRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> TenantAuthConfigResponse:
    """Create authentication configuration for a company."""
    service = get_tenant_auth_service(db)
    
    try:
        config = service.create_auth_config(company_id, config_request.dict())
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/config/{company_id}",
    response_model=TenantAuthConfigResponse,
    summary="Get auth config",
    description="Get authentication configuration for a company.",
    tags=["Tenant Auth Config"]
)
async def get_auth_config(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> TenantAuthConfigResponse:
    """Get authentication configuration for a company."""
    service = get_tenant_auth_service(db)
    
    config = service.get_auth_config(company_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auth configuration not found"
        )
    
    return config


@router.post(
    "/login",
    response_model=TenantLoginResponse,
    summary="Tenant login",
    description="Login with tenant context.",
    tags=["Tenant Auth"]
)
async def tenant_login(
    login_request: TenantLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TenantLoginResponse:
    """Login with tenant context."""
    service = get_tenant_auth_service(db)
    
    # Get client info
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    
    try:
        # Log login attempt
        service.log_login_attempt(
            email=login_request.email,
            success=False,  # Will update if successful
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # TODO: Implement actual authentication logic
        # This is a simplified version
        
        # Mock response for now
        return TenantLoginResponse(
            access_token="mock_token",
            expires_in=3600,
            user_id=UUID("12345678-1234-5678-9012-123456789012"),
            company_id=UUID("12345678-1234-5678-9012-123456789012"),
            company_name="Mock Company"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.post(
    "/logout",
    summary="Logout",
    description="Logout and terminate session.",
    tags=["Tenant Auth"]
)
async def logout(
    session_token: str,
    db: Session = Depends(get_db),
) -> dict:
    """Logout and terminate session."""
    service = get_tenant_auth_service(db)
    
    success = service.terminate_session(session_token, "user_logout")
    
    if success:
        return {"message": "Logged out successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.get(
    "/sessions/{user_id}",
    response_model=List[TenantSessionResponse],
    summary="Get user sessions",
    description="Get active sessions for a user.",
    tags=["Tenant Sessions"]
)
async def get_user_sessions(
    user_id: UUID,
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[TenantSessionResponse]:
    """Get active sessions for a user."""
    # TODO: Implement session retrieval
    return []


@router.delete(
    "/sessions/{user_id}/terminate-all",
    summary="Terminate all sessions",
    description="Terminate all sessions for a user.",
    tags=["Tenant Sessions"]
)
async def terminate_all_sessions(
    user_id: UUID,
    company_id: UUID,
    except_current: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> dict:
    """Terminate all sessions for a user."""
    service = get_tenant_auth_service(db)
    
    except_token = None  # TODO: Get current session token
    if except_current:
        except_token = "current_token"
    
    service.terminate_all_user_sessions(user_id, company_id, except_token)
    
    return {"message": "All sessions terminated"}


@router.post(
    "/password-reset",
    summary="Request password reset",
    description="Request password reset with company branding.",
    tags=["Password Reset"]
)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Request password reset with company branding."""
    service = get_tenant_auth_service(db)
    
    # TODO: Implement password reset logic
    # This would involve:
    # 1. Find user by email and company
    # 2. Create reset token
    # 3. Send branded email
    
    return {"message": "Password reset email sent"}


@router.post(
    "/password-reset/confirm",
    summary="Confirm password reset",
    description="Confirm password reset with token.",
    tags=["Password Reset"]
)
async def confirm_password_reset(
    confirm_request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Confirm password reset with token."""
    service = get_tenant_auth_service(db)
    
    # Validate token
    reset_token = service.validate_password_reset_token(confirm_request.token)
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # TODO: Update user password
    # Mark token as used
    service.use_password_reset_token(confirm_request.token)
    
    return {"message": "Password reset successfully"}


@router.post(
    "/oauth/{company_id}",
    response_model=OAuthProviderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create OAuth provider",
    description="Create OAuth provider configuration.",
    tags=["OAuth"]
)
async def create_oauth_provider(
    company_id: UUID,
    provider_request: OAuthProviderRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> OAuthProviderResponse:
    """Create OAuth provider configuration."""
    service = get_tenant_auth_service(db)
    
    try:
        provider = service.create_oauth_provider(company_id, provider_request.dict())
        return provider
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/oauth/{company_id}",
    response_model=List[OAuthProviderResponse],
    summary="Get OAuth providers",
    description="Get OAuth providers for a company.",
    tags=["OAuth"]
)
async def get_oauth_providers(
    company_id: UUID,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[OAuthProviderResponse]:
    """Get OAuth providers for a company."""
    service = get_tenant_auth_service(db)
    
    providers = service.get_oauth_providers(company_id, active_only)
    return providers


@router.get(
    "/companies/{user_id}",
    response_model=CompanySelectionResponse,
    summary="Get user companies",
    description="Get companies available to a user for selection.",
    tags=["Company Selection"]
)
async def get_user_companies(
    user_id: UUID,
    db: Session = Depends(get_db),
) -> CompanySelectionResponse:
    """Get companies available to a user for selection."""
    # TODO: Implement company selection logic
    return CompanySelectionResponse(
        companies=[],
        default_company_id=None
    )


@router.get(
    "/login-attempts",
    response_model=List[LoginAttemptResponse],
    summary="Get login attempts",
    description="Get login attempts for monitoring.",
    tags=["Security Monitoring"]
)
async def get_login_attempts(
    company_id: Optional[UUID] = None,
    email: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[LoginAttemptResponse]:
    """Get login attempts for monitoring."""
    service = get_tenant_auth_service(db)
    
    attempts = service.get_login_attempts(company_id, email, limit)
    return attempts


@router.post(
    "/cleanup-sessions",
    summary="Cleanup expired sessions",
    description="Clean up expired sessions.",
    tags=["Maintenance"]
)
async def cleanup_expired_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> dict:
    """Clean up expired sessions."""
    service = get_tenant_auth_service(db)
    
    cleaned_count = service.cleanup_expired_sessions()
    
    return {
        "message": f"Cleaned up {cleaned_count} expired sessions",
        "cleaned_count": cleaned_count
    }