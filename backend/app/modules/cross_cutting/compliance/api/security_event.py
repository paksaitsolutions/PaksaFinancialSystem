"""
Paksa Financial System - Security Event API Endpoints
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

API endpoints for managing and monitoring security events.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ....core.security import get_current_active_admin, get_current_active_user
from ....db.session import get_db
from ....schemas.user import UserInDB
from .. import models, schemas, exceptions
from ..services import SecurityEventService, AuditService

# Create router with dependencies
router = APIRouter(
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

def paksa_get_security_event_service(db: Session = Depends(get_db)) -> SecurityEventService:
    """Dependency to get an instance of SecurityEventService."""
    return SecurityEventService(db)

def paksa_get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Dependency to get an instance of AuditService."""
    return AuditService(db)

@router.post("/events", response_model=schemas.SecurityEvent, status_code=status.HTTP_201_CREATED)
async def paksa_create_security_event(
    event_data: schemas.SecurityEventCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Create a new security event.
    
    This endpoint is typically called by internal systems to log security-related events.
    Requires authentication but can be called by any authenticated user.
    """
    try:
        event_service = SecurityEventService(db)
        
        # Create the security event
        event = event_service.create_event(
            event_type=event_data.event_type,
            severity=event_data.severity,
            source=event_data.source,
            details=event_data.details,
            user_id=current_user.id if current_user else None,
            ip_address=event_data.ip_address,
            user_agent=event_data.user_agent,
            metadata=event_data.metadata
        )
        
        # No audit log here to avoid circular logging, but we could add it if needed
        
        # Check if this event triggers any alerts
        triggered_alerts = event_service.check_event_for_alerts(event)
        
        # In a real implementation, we would notify relevant parties about the alert
        
        return event
        
    except exceptions.SecurityEventError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create security event: {str(e)}"
        )

@router.get("/events", response_model=schemas.PaksaListResponse[schemas.SecurityEvent])
async def paksa_list_security_events(
    event_type: Optional[models.SecurityEventType] = None,
    severity: Optional[models.SeverityLevel] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    source: Optional[str] = None,
    user_id: Optional[UUID] = None,
    ip_address: Optional[str] = None,
    resolved: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    order_by: str = "timestamp",
    order_desc: bool = True,
    event_service: SecurityEventService = Depends(paksa_get_security_event_service),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    List security events with filtering and pagination.
    
    Regular users can only see their own events. Administrators can see all events.
    """
    try:
        # Regular users can only see their own events
        if not current_user.is_superuser:
            user_id = current_user.id
        
        # Get the list of events
        events, total = event_service.list_events(
            event_type=event_type,
            severity=severity,
            start_date=start_date,
            end_date=end_date,
            source=source,
            user_id=user_id,
            ip_address=ip_address,
            resolved=resolved,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc
        )
        
        return schemas.PaksaListResponse(
            items=events,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch security events: {str(e)}"
        )

@router.get("/events/{event_id}", response_model=schemas.SecurityEvent)
async def paksa_get_security_event(
    event_id: UUID,
    event_service: SecurityEventService = Depends(paksa_get_security_event_service),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Retrieve a specific security event by ID.
    
    Regular users can only see their own events. Administrators can see all events.
    """
    try:
        event = event_service.get_event(event_id)
        
        # Check if the current user has permission to view this event
        if not current_user.is_superuser and (not event.user_id or str(event.user_id) != str(current_user.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this event"
            )
            
        return event
        
    except exceptions.SecurityEventNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch security event: {str(e)}"
        )

@router.put("/events/{event_id}/resolve", response_model=schemas.SecurityEvent)
async def paksa_resolve_security_event(
    event_id: UUID,
    resolution_data: schemas.SecurityEventResolution,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Resolve a security event.
    
    Only accessible by administrators.
    """
    try:
        event_service = SecurityEventService(db)
        audit_service = AuditService(db)
        
        # Resolve the event
        event = event_service.resolve_event(
            event_id=event_id,
            resolved_by=current_user.id,
            resolution=resolution_data.resolution,
            resolution_notes=resolution_data.notes
        )
        
        # Log the resolution
        audit_service.create_audit_log(
            action=models.AuditActionType.UPDATE,
            resource_type="SecurityEvent",
            resource_id=str(event_id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "action": "resolved",
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "resolution": resolution_data.resolution
            }
        )
        
        return event
        
    except exceptions.SecurityEventNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except exceptions.SecurityEventError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve security event: {str(e)}"
        )

@router.get("/events/summary", response_model=List[schemas.SecurityEventSummary])
async def paksa_get_security_events_summary(
    group_by: str = "day",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[models.SecurityEventType] = None,
    severity: Optional[models.SeverityLevel] = None,
    source: Optional[str] = None,
    event_service: SecurityEventService = Depends(paksa_get_security_event_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Get a summary of security events grouped by time period and other dimensions.
    
    Only accessible by administrators.
    """
    try:
        summary = event_service.get_events_summary(
            group_by=group_by,
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            severity=severity,
            source=source
        )
        return summary
    except exceptions.SecurityEventError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate security events summary: {str(e)}"
        )

@router.get("/alerts", response_model=List[schemas.SecurityAlert])
async def paksa_list_security_alerts(
    status: Optional[models.AlertStatus] = None,
    severity: Optional[models.SeverityLevel] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_service: SecurityEventService = Depends(paksa_get_security_event_service),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    List security alerts with filtering and pagination.
    
    Only accessible by administrators.
    """
    try:
        alerts = event_service.list_alerts(
            status=status,
            severity=severity,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch security alerts: {str(e)}"
        )

@router.post("/alerts/{alert_id}/acknowledge", response_model=schemas.SecurityAlert)
async def paksa_acknowledge_security_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Acknowledge a security alert.
    
    Only accessible by administrators.
    """
    try:
        event_service = SecurityEventService(db)
        audit_service = AuditService(db)
        
        # Acknowledge the alert
        alert = event_service.acknowledge_alert(
            alert_id=alert_id,
            acknowledged_by=current_user.id
        )
        
        # Log the acknowledgment
        audit_service.create_audit_log(
            action=models.AuditActionType.UPDATE,
            resource_type="SecurityAlert",
            resource_id=str(alert_id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "action": "acknowledged",
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value
            }
        )
        
        return alert
        
    except exceptions.SecurityAlertNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except exceptions.SecurityAlertError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge security alert: {str(e)}"
        )
