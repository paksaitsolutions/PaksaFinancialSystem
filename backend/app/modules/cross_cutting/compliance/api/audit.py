"""
Paksa Financial System - Audit API Endpoints
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

API endpoints for audit log operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ....core.security import get_current_active_admin
from ....db.session import get_db
from ....schemas.user import UserInDB
from .. import models, schemas
from ..services import AuditService

# Create router with dependencies
router = APIRouter(
    dependencies=[Depends(get_current_active_admin)],
    responses={404: {"description": "Not found"}},
)

def paksa_get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Dependency to get an instance of AuditService."""
    return AuditService(db)

@router.get("/logs", response_model=schemas.PaksaListResponse[schemas.AuditLog])
async def paksa_list_audit_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[UUID] = None,
    action: Optional[models.AuditActionType] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    status_code: Optional[int] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    order_by: str = "timestamp",
    order_desc: bool = True,
    audit_service: AuditService = Depends(paksa_get_audit_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    List audit logs with filtering and pagination.
    
    Only accessible by administrators.
    """
    try:
        logs, total = audit_service.list_audit_logs(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status_code=status_code,
            username=username,
            ip_address=ip_address,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc
        )
        
        return schemas.PaksaListResponse(
            items=logs,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch audit logs: {str(e)}"
        )

@router.get("/logs/{log_id}", response_model=schemas.AuditLog)
async def paksa_get_audit_log(
    log_id: UUID,
    audit_service: AuditService = Depends(paksa_get_audit_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Retrieve a specific audit log entry by ID.
    
    Only accessible by administrators.
    """
    try:
        log = audit_service.get_audit_log(log_id)
        return log
    except exceptions.AuditLogNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch audit log: {str(e)}"
        )

@router.get("/summary", response_model=List[schemas.AuditSummary])
async def paksa_get_audit_summary(
    start_date: datetime,
    end_date: datetime,
    group_by: str = "day",
    user_id: Optional[UUID] = None,
    action: Optional[models.AuditActionType] = None,
    resource_type: Optional[str] = None,
    audit_service: AuditService = Depends(paksa_get_audit_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Get a summary of audit logs grouped by time period.
    
    Only accessible by administrators.
    """
    try:
        summary = audit_service.get_audit_summary(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
            user_id=user_id,
            action=action,
            resource_type=resource_type
        )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate audit summary: {str(e)}"
        )

@router.delete("/logs/cleanup", status_code=status.HTTP_204_NO_CONTENT)
async def paksa_cleanup_old_logs(
    older_than_days: int = 365,
    batch_size: int = 1000,
    audit_service: AuditService = Depends(paksa_get_audit_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Delete audit logs older than the specified number of days.
    
    Only accessible by administrators with appropriate permissions.
    """
    try:
        count = audit_service.cleanup_old_logs(
            older_than_days=older_than_days,
            batch_size=batch_size
        )
        return {"deleted_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to clean up old logs: {str(e)}"
        )
