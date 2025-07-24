"""
Audit logging API endpoints.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.audit_schemas import (
    AuditLogResponse,
    AuditLogRequest,
    AuditLogFilter,
    AuditStatisticsResponse,
    AuditConfigResponse,
    UserActivityResponse,
    ResourceHistoryResponse
)
from app.services.audit.audit_service import AuditService

router = APIRouter()


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Get an instance of the audit service."""
    return AuditService(db)


@router.post(
    "/log",
    response_model=AuditLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create audit log",
    description="Create a new audit log entry.",
    tags=["Audit Logging"]
)
async def create_audit_log(
    log_request: AuditLogRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> AuditLogResponse:
    """Create a new audit log entry."""
    service = get_audit_service(db)
    
    try:
        audit_log = service.log_action(
            action=log_request.action,
            resource_type=log_request.resource_type,
            user_id=current_user.id,
            resource_id=log_request.resource_id,
            old_values=log_request.old_values,
            new_values=log_request.new_values,
            description=log_request.description,
            metadata=log_request.metadata
        )
        
        return audit_log
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/logs",
    response_model=List[AuditLogResponse],
    summary="Get audit logs",
    description="Get audit logs with optional filters.",
    tags=["Audit Logging"]
)
async def get_audit_logs(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    action: Optional[str] = Query(None, description="Filter by action"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[AuditLogResponse]:
    """Get audit logs with optional filters."""
    service = get_audit_service(db)
    
    logs = service.get_audit_logs(
        user_id=user_id,
        resource_type=resource_type,
        action=action,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return logs


@router.get(
    "/user/{user_id}/activity",
    response_model=UserActivityResponse,
    summary="Get user activity",
    description="Get recent activity for a specific user.",
    tags=["Audit Logging"]
)
async def get_user_activity(
    user_id: UUID,
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> UserActivityResponse:
    """Get recent activity for a specific user."""
    service = get_audit_service(db)
    
    logs = service.get_user_activity(user_id, days)
    
    return UserActivityResponse(
        user_id=user_id,
        logs=logs,
        total_actions=len(logs),
        period_days=days
    )


@router.get(
    "/resource/{resource_type}/{resource_id}/history",
    response_model=ResourceHistoryResponse,
    summary="Get resource history",
    description="Get audit history for a specific resource.",
    tags=["Audit Logging"]
)
async def get_resource_history(
    resource_type: str,
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ResourceHistoryResponse:
    """Get audit history for a specific resource."""
    service = get_audit_service(db)
    
    logs = service.get_resource_history(resource_type, resource_id)
    
    return ResourceHistoryResponse(
        resource_type=resource_type,
        resource_id=resource_id,
        logs=logs,
        total_changes=len(logs)
    )


@router.get(
    "/statistics",
    response_model=AuditStatisticsResponse,
    summary="Get audit statistics",
    description="Get audit statistics for a specified period.",
    tags=["Audit Logging"]
)
async def get_audit_statistics(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> AuditStatisticsResponse:
    """Get audit statistics for a specified period."""
    service = get_audit_service(db)
    
    stats = service.get_audit_statistics(days)
    
    return AuditStatisticsResponse(**stats)


@router.get(
    "/config",
    response_model=AuditConfigResponse,
    summary="Get audit configuration",
    description="Get the active audit configuration.",
    tags=["Audit Configuration"]
)
async def get_audit_config(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> AuditConfigResponse:
    """Get the active audit configuration."""
    service = get_audit_service(db)
    
    config = service.get_active_config()
    return config


@router.post(
    "/cleanup",
    summary="Cleanup old logs",
    description="Clean up old audit logs based on retention policy.",
    tags=["Audit Maintenance"]
)
async def cleanup_old_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Clean up old audit logs based on retention policy."""
    service = get_audit_service(db)
    
    cleaned_count = service.cleanup_old_logs()
    
    return {
        "message": f"Cleaned up {cleaned_count} old audit logs",
        "cleaned_count": cleaned_count
    }