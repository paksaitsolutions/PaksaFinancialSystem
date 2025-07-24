"""
Operations API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.services.operations.monitoring_service import MonitoringService
from app.services.operations.logging_service import LoggingService
from app.services.operations.alerting_service import AlertingService
from app.services.operations.backup_service import BackupService

router = APIRouter()


@router.get(
    "/health",
    summary="System health check",
    description="Get system health status and metrics.",
    tags=["Operations"]
)
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get system health status."""
    service = MonitoringService(db)
    return service.get_system_health()


@router.get(
    "/logs",
    summary="Get system logs",
    description="Retrieve system logs with optional filtering.",
    tags=["Operations"]
)
async def get_system_logs(
    level: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get system logs."""
    service = LoggingService(db)
    return service.get_logs(level, limit)


@router.get(
    "/alerts",
    summary="Get active alerts",
    description="Get all active system alerts.",
    tags=["Operations"]
)
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get active system alerts."""
    service = AlertingService(db)
    return service.get_active_alerts()


@router.post(
    "/alerts/{alert_id}/resolve",
    summary="Resolve alert",
    description="Mark an alert as resolved.",
    tags=["Operations"]
)
async def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Resolve a system alert."""
    service = AlertingService(db)
    success = service.resolve_alert(alert_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return {"message": "Alert resolved successfully"}


@router.post(
    "/backup",
    summary="Create backup",
    description="Create a database backup.",
    tags=["Operations"]
)
async def create_backup(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Create a database backup."""
    service = BackupService(db)
    backup_record = service.create_database_backup()
    return backup_record


@router.get(
    "/backups",
    summary="Get backup history",
    description="Get backup history and status.",
    tags=["Operations"]
)
async def get_backup_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get backup history."""
    service = BackupService(db)
    return service.get_backup_history(limit)