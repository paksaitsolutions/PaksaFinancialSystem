"""
Data retention API endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.retention_schemas import (
    DataRetentionPolicyRequest,
    DataRetentionPolicyResponse,
    RetentionExecutionResponse,
    RetentionDashboardResponse
)
from app.services.retention.retention_service import DataRetentionService

router = APIRouter()


def get_retention_service(db: Session = Depends(get_db)) -> DataRetentionService:
    """Get an instance of the retention service."""
    return DataRetentionService(db)


@router.post(
    "/policies",
    response_model=DataRetentionPolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create retention policy",
    description="Create a new data retention policy.",
    tags=["Data Retention"]
)
async def create_policy(
    policy_request: DataRetentionPolicyRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> DataRetentionPolicyResponse:
    """Create a new data retention policy."""
    service = get_retention_service(db)
    
    try:
        policy = service.create_policy(policy_request.dict(), current_user.id)
        return policy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/policies",
    response_model=List[DataRetentionPolicyResponse],
    summary="List retention policies",
    description="List data retention policies.",
    tags=["Data Retention"]
)
async def list_policies(
    active_only: bool = Query(True, description="Show only active policies"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[DataRetentionPolicyResponse]:
    """List data retention policies."""
    service = get_retention_service(db)
    
    policies = service.list_policies(active_only=active_only)
    return policies


@router.post(
    "/policies/{policy_id}/execute",
    response_model=RetentionExecutionResponse,
    summary="Execute retention policy",
    description="Execute a specific data retention policy.",
    tags=["Data Retention"]
)
async def execute_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> RetentionExecutionResponse:
    """Execute a specific data retention policy."""
    service = get_retention_service(db)
    
    try:
        execution = service.execute_policy(policy_id)
        return execution
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/execute-all",
    response_model=List[RetentionExecutionResponse],
    summary="Execute all due policies",
    description="Execute all data retention policies that are due.",
    tags=["Data Retention"]
)
async def execute_all_policies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[RetentionExecutionResponse]:
    """Execute all data retention policies that are due."""
    service = get_retention_service(db)
    
    executions = service.execute_all_policies()
    return executions


@router.get(
    "/executions",
    response_model=List[RetentionExecutionResponse],
    summary="Get execution history",
    description="Get data retention execution history.",
    tags=["Data Retention"]
)
async def get_execution_history(
    policy_id: Optional[UUID] = Query(None, description="Filter by policy ID"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[RetentionExecutionResponse]:
    """Get data retention execution history."""
    service = get_retention_service(db)
    
    executions = service.get_execution_history(policy_id=policy_id, limit=limit)
    return executions


@router.post(
    "/initialize",
    summary="Initialize default policies",
    description="Initialize default data retention policies.",
    tags=["Data Retention"]
)
async def initialize_default_policies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Initialize default data retention policies."""
    service = get_retention_service(db)
    
    try:
        service.initialize_default_policies()
        return {"message": "Default retention policies initialized successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/dashboard",
    response_model=RetentionDashboardResponse,
    summary="Get retention dashboard",
    description="Get data retention dashboard information.",
    tags=["Data Retention"]
)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> RetentionDashboardResponse:
    """Get data retention dashboard information."""
    service = get_retention_service(db)
    
    # Get policy statistics
    all_policies = service.list_policies(active_only=False)
    active_policies = service.list_policies(active_only=True)
    
    from datetime import datetime
    policies_due = len([p for p in active_policies if p.next_execution and p.next_execution <= datetime.utcnow()])
    
    # Get recent executions
    recent_executions = service.get_execution_history(limit=10)
    
    # Calculate totals
    total_records_processed = sum(e.records_processed for e in recent_executions if e.execution_date.date() == datetime.utcnow().date())
    
    # Estimate storage saved (simplified calculation)
    storage_saved_mb = sum(e.records_deleted + e.records_archived for e in recent_executions) * 0.001  # Rough estimate
    
    return RetentionDashboardResponse(
        total_policies=len(all_policies),
        active_policies=len(active_policies),
        policies_due=policies_due,
        recent_executions=recent_executions,
        total_records_processed=total_records_processed,
        storage_saved_mb=storage_saved_mb
    )