"""
Backup and restore API endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.backup_schemas import (
    BackupRequest,
    BackupResponse,
    RestoreRequest,
    RestoreResponse,
    BackupScheduleRequest,
    BackupScheduleResponse,
    BackupDashboardResponse
)
from app.services.backup.backup_service import BackupService

router = APIRouter()


def get_backup_service(db: Session = Depends(get_db)) -> BackupService:
    """Get an instance of the backup service."""
    return BackupService(db)


@router.post(
    "/backups",
    response_model=BackupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create backup",
    description="Create a new database backup.",
    tags=["Backup"]
)
async def create_backup(
    backup_request: BackupRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> BackupResponse:
    """Create a new database backup."""
    service = get_backup_service(db)
    
    try:
        backup = service.create_backup(
            backup_name=backup_request.backup_name,
            backup_type=backup_request.backup_type,
            initiated_by=current_user.id,
            tables=backup_request.tables
        )
        return backup
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/backups",
    response_model=List[BackupResponse],
    summary="List backups",
    description="List database backups.",
    tags=["Backup"]
)
async def list_backups(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[BackupResponse]:
    """List database backups."""
    service = get_backup_service(db)
    
    backups = service.list_backups(limit=limit)
    return backups


@router.get(
    "/backups/{backup_id}",
    response_model=BackupResponse,
    summary="Get backup",
    description="Get a backup by ID.",
    tags=["Backup"]
)
async def get_backup(
    backup_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> BackupResponse:
    """Get a backup by ID."""
    service = get_backup_service(db)
    
    backup = service.get_backup(backup_id)
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup not found"
        )
    
    return backup


@router.post(
    "/restore",
    response_model=RestoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Restore backup",
    description="Restore from a backup.",
    tags=["Restore"]
)
async def restore_backup(
    restore_request: RestoreRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> RestoreResponse:
    """Restore from a backup."""
    service = get_backup_service(db)
    
    try:
        restore_op = service.restore_backup(
            backup_id=restore_request.backup_id,
            restore_name=restore_request.restore_name,
            initiated_by=current_user.id,
            tables_to_restore=restore_request.tables_to_restore,
            overwrite_existing=restore_request.overwrite_existing
        )
        return restore_op
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/restore-operations",
    response_model=List[RestoreResponse],
    summary="List restore operations",
    description="List restore operations.",
    tags=["Restore"]
)
async def list_restore_operations(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[RestoreResponse]:
    """List restore operations."""
    service = get_backup_service(db)
    
    operations = service.list_restore_operations(limit=limit)
    return operations


@router.post(
    "/schedules",
    response_model=BackupScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create backup schedule",
    description="Create a backup schedule.",
    tags=["Backup Schedule"]
)
async def create_schedule(
    schedule_request: BackupScheduleRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> BackupScheduleResponse:
    """Create a backup schedule."""
    service = get_backup_service(db)
    
    try:
        schedule = service.create_schedule(schedule_request.dict(), current_user.id)
        return schedule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/schedules",
    response_model=List[BackupScheduleResponse],
    summary="List backup schedules",
    description="List backup schedules.",
    tags=["Backup Schedule"]
)
async def list_schedules(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[BackupScheduleResponse]:
    """List backup schedules."""
    service = get_backup_service(db)
    
    schedules = service.list_schedules(active_only=active_only)
    return schedules


@router.post(
    "/cleanup",
    summary="Cleanup old backups",
    description="Clean up old backup files.",
    tags=["Backup"]
)
async def cleanup_old_backups(
    retention_days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Clean up old backup files."""
    service = get_backup_service(db)
    
    cleaned_count = service.cleanup_old_backups(retention_days=retention_days)
    
    return {
        "message": f"Cleaned up {cleaned_count} old backups",
        "cleaned_count": cleaned_count
    }


@router.get(
    "/dashboard",
    response_model=BackupDashboardResponse,
    summary="Get backup dashboard",
    description="Get backup dashboard information.",
    tags=["Backup"]
)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> BackupDashboardResponse:
    """Get backup dashboard information."""
    service = get_backup_service(db)
    
    # Get backup statistics
    all_backups = service.list_backups(limit=1000)
    successful_backups = len([b for b in all_backups if b.status == "completed"])
    failed_backups = len([b for b in all_backups if b.status == "failed"])
    
    # Calculate total storage
    total_storage_mb = sum(b.file_size or 0 for b in all_backups) / (1024 * 1024)
    
    # Get recent backups
    recent_backups = service.list_backups(limit=5)
    
    # Get schedule count
    schedules = service.list_schedules(active_only=True)
    
    # Get last backup date
    last_backup_date = recent_backups[0].created_at if recent_backups else None
    
    return BackupDashboardResponse(
        total_backups=len(all_backups),
        successful_backups=successful_backups,
        failed_backups=failed_backups,
        total_storage_mb=total_storage_mb,
        recent_backups=recent_backups,
        active_schedules=len(schedules),
        last_backup_date=last_backup_date
    )