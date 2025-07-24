"""
Session management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.session_schemas import (
    SessionResponse,
    SessionValidationResponse,
    SessionCreateRequest,
    SessionExtendRequest,
    SessionTerminateRequest,
    SessionConfigResponse,
    UserSessionsResponse,
    SessionStatsResponse
)
from app.services.auth.session_service import SessionService

router = APIRouter()


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    """Get an instance of the session service."""
    return SessionService(db)


@router.post(
    "/create",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create session",
    description="Create a new user session.",
    tags=["Session Management"]
)
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db),
) -> SessionResponse:
    """Create a new user session."""
    service = get_session_service(db)
    
    try:
            session = service.create_session(
                user_id=request.user_id,
                company_id=request.company_id,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
                remember_me=request.remember_me
            )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/validate/{session_token}",
    response_model=SessionValidationResponse,
    summary="Validate session",
    description="Validate a session token.",
    tags=["Session Management"]
)
async def validate_session(
    session_token: str,
    db: Session = Depends(get_db),
) -> SessionValidationResponse:
    """Validate a session token."""
    service = get_session_service(db)
    
    validation = service.validate_session(session_token)
    
    return SessionValidationResponse(
        valid=validation['valid'],
        reason=validation.get('reason'),
        user_id=validation.get('user_id'),
        expires_at=validation.get('expires_at')
    )


@router.post(
    "/extend/{session_token}",
    response_model=SessionResponse,
    summary="Extend session",
    description="Extend session expiration.",
    tags=["Session Management"]
)
async def extend_session(
    session_token: str,
    request: SessionExtendRequest,
    db: Session = Depends(get_db),
) -> SessionResponse:
    """Extend session expiration."""
    service = get_session_service(db)
    
    try:
        session = service.extend_session(session_token, request.duration_minutes)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/terminate/{session_token}",
    summary="Terminate session",
    description="Terminate a specific session.",
    tags=["Session Management"]
)
async def terminate_session(
    session_token: str,
    request: SessionTerminateRequest,
    db: Session = Depends(get_db),
):
    """Terminate a specific session."""
    service = get_session_service(db)
    
    success = service.terminate_session(session_token, request.reason)
    
    if success:
        return {"message": "Session terminated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.get(
    "/user/{user_id}",
    response_model=UserSessionsResponse,
    summary="Get user sessions",
    description="Get all sessions for a user.",
    tags=["Session Management"]
)
async def get_user_sessions(
    user_id: str,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> UserSessionsResponse:
    """Get all sessions for a user."""
    service = get_session_service(db)
    
    sessions = service.get_user_sessions(user_id, active_only)
    active_count = len([s for s in sessions if s.is_active()])
    
    return UserSessionsResponse(
        sessions=sessions,
        total_count=len(sessions),
        active_count=active_count
    )


@router.post(
    "/terminate-user/{user_id}",
    summary="Terminate user sessions",
    description="Terminate all sessions for a user.",
    tags=["Session Management"]
)
async def terminate_user_sessions(
    user_id: str,
    except_session: str = None,
    reason: str = "Admin action",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Terminate all sessions for a user."""
    service = get_session_service(db)
    
    terminated_count = service.terminate_user_sessions(user_id, except_session, reason)
    
    return {
        "message": f"Terminated {terminated_count} sessions",
        "terminated_count": terminated_count
    }


@router.post(
    "/cleanup",
    summary="Cleanup expired sessions",
    description="Clean up expired sessions.",
    tags=["Session Management"]
)
async def cleanup_expired_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Clean up expired sessions."""
    service = get_session_service(db)
    
    cleaned_count = service.cleanup_expired_sessions()
    
    return {
        "message": f"Cleaned up {cleaned_count} expired sessions",
        "cleaned_count": cleaned_count
    }


@router.get(
    "/config",
    response_model=SessionConfigResponse,
    summary="Get session configuration",
    description="Get the active session configuration.",
    tags=["Session Configuration"]
)
async def get_session_config(
    db: Session = Depends(get_db),
) -> SessionConfigResponse:
    """Get the active session configuration."""
    service = get_session_service(db)
    
    config = service.get_active_config()
    return config


@router.get(
    "/fresh-login-required/{session_token}",
    summary="Check fresh login requirement",
    description="Check if fresh login is required for sensitive operations.",
    tags=["Session Management"]
)
async def check_fresh_login_required(
    session_token: str,
    db: Session = Depends(get_db),
):
    """Check if fresh login is required for sensitive operations."""
    service = get_session_service(db)
    
    required = service.is_fresh_login_required(session_token)
    
    return {
        "fresh_login_required": required,
        "message": "Fresh login required for sensitive operations" if required else "Session is fresh"
    }