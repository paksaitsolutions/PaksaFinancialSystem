"""
Reconciliation API Endpoints

This module provides the API endpoints for account reconciliation functionality.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import tempfile

from app.api.dependencies import get_db, get_current_user
from app.schemas.user import UserInDB
from app.schemas.common import PaginatedResponse

from ...services.reconciliation.service import ReconciliationService
from ...services.reconciliation.item_service import ReconciliationItemService
from ...services.reconciliation.rule_service import ReconciliationRuleService
from ...services.reconciliation.audit_service import ReconciliationAuditService

from ...schemas.reconciliation import (
    Reconciliation as ReconciliationSchema,
    ReconciliationCreate,
    ReconciliationUpdate,
    ReconciliationItem as ReconciliationItemSchema,
    ReconciliationItemCreate,
    ReconciliationItemUpdate,
    ReconciliationRule as ReconciliationRuleSchema,
    ReconciliationRuleCreate,
    ReconciliationRuleUpdate,
    ReconciliationAuditLog as ReconciliationAuditLogSchema,
    ReconciliationStatus,
    ReconciliationMatchType,
    ReconciliationExportFormat
)

router = APIRouter()

# Helper function to get reconciliation service
def get_reconciliation_service(db: Session = Depends(get_db)):
    return ReconciliationService(db)

def get_reconciliation_item_service(db: Session = Depends(get_db)):
    return ReconciliationItemService(db)

def get_reconciliation_rule_service(db: Session = Depends(get_db)):
    return ReconciliationRuleService(db)

def get_reconciliation_audit_service(db: Session = Depends(get_db)):
    return ReconciliationAuditService(db)

# Reconciliation Endpoints

@router.post(
    "/reconciliations/",
    response_model=ReconciliationSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reconciliation",
    description="Create a new reconciliation for an account with the specified date range and statement balance."
)
async def create_reconciliation(
    reconciliation: ReconciliationCreate,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        return service.create_reconciliation(reconciliation, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/reconciliations/",
    response_model=PaginatedResponse[ReconciliationSchema],
    summary="List reconciliations",
    description="List all reconciliations with optional filtering and pagination."
)
async def list_reconciliations(
    account_id: Optional[UUID] = Query(None, description="Filter by account ID"),
    status: Optional[ReconciliationStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (greater than or equal)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (less than or equal)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        items, total = service.list_reconciliations(
            user_id=current_user.id,
            account_id=account_id,
            status=status.value if status else None,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/reconciliations/{reconciliation_id}",
    response_model=ReconciliationSchema,
    summary="Get a reconciliation",
    description="Get a reconciliation by ID."
)
async def get_reconciliation(
    reconciliation_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        return service.get_reconciliation(reconciliation_id, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/reconciliations/{reconciliation_id}",
    response_model=ReconciliationSchema,
    summary="Update a reconciliation",
    description="Update a reconciliation by ID."
)
async def update_reconciliation(
    reconciliation_id: UUID,
    reconciliation: ReconciliationUpdate,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        return service.update_reconciliation(reconciliation_id, reconciliation, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/reconciliations/{reconciliation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a reconciliation",
    description="Delete a reconciliation by ID."
)
async def delete_reconciliation(
    reconciliation_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        service.delete_reconciliation(reconciliation_id, current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Reconciliation Item Endpoints

@router.post(
    "/reconciliations/{reconciliation_id}/items",
    response_model=ReconciliationItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add an item to a reconciliation",
    description="Add an item to a reconciliation."
)
async def add_reconciliation_item(
    reconciliation_id: UUID,
    item: ReconciliationItemCreate,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationItemService = Depends(get_reconciliation_item_service)
):
    try:
        return service.add_reconciliation_item(reconciliation_id, item, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/reconciliations/items/{item_id}",
    response_model=ReconciliationItemSchema,
    summary="Update a reconciliation item",
    description="Update a reconciliation item by ID."
)
async def update_reconciliation_item(
    item_id: UUID,
    item: ReconciliationItemUpdate,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationItemService = Depends(get_reconciliation_item_service)
):
    try:
        return service.update_reconciliation_item(item_id, item, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/reconciliations/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a reconciliation item",
    description="Delete a reconciliation item by ID."
)
async def delete_reconciliation_item(
    item_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationItemService = Depends(get_reconciliation_item_service)
):
    try:
        service.delete_reconciliation_item(item_id, current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Reconciliation Rule Endpoints

@router.post(
    "/reconciliation-rules/",
    response_model=ReconciliationRuleSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reconciliation rule",
    description="Create a new reconciliation rule for automatic matching."
)
async def create_reconciliation_rule(
    rule: ReconciliationRuleCreate,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationRuleService = Depends(get_reconciliation_rule_service)
):
    try:
        return service.create_rule(rule, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/reconciliation-rules/",
    response_model=List[ReconciliationRuleSchema],
    summary="List reconciliation rules",
    description="List all reconciliation rules with optional filtering."
)
async def list_reconciliation_rules(
    account_id: Optional[UUID] = Query(None, description="Filter by account ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationRuleService = Depends(get_reconciliation_rule_service)
):
    try:
        rules, _ = service.list_rules(
            user_id=current_user.id,
            account_id=account_id,
            is_active=is_active
        )
        return rules
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/reconciliation-rules/{rule_id}",
    response_model=ReconciliationRuleSchema,
    summary="Get a reconciliation rule",
    description="Get a reconciliation rule by ID."
)
async def get_reconciliation_rule(
    rule_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationRuleService = Depends(get_reconciliation_rule_service)
):
    try:
        return service.get_rule(rule_id, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/reconciliation-rules/{rule_id}",
    response_model=ReconciliationRuleSchema,
    summary="Update a reconciliation rule",
    description="Update a reconciliation rule by ID."
)
async def update_reconciliation_rule(
    rule_id: UUID,
    rule: ReconciliationRuleUpdate,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationRuleService = Depends(get_reconciliation_rule_service)
):
    try:
        return service.update_rule(rule_id, rule, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/reconciliation-rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a reconciliation rule",
    description="Delete a reconciliation rule by ID."
)
async def delete_reconciliation_rule(
    rule_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationRuleService = Depends(get_reconciliation_rule_service)
):
    try:
        service.delete_rule(rule_id, current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Reconciliation Audit Log Endpoints

@router.get(
    "/reconciliations/{reconciliation_id}/audit-logs",
    response_model=List[ReconciliationAuditLogSchema],
    summary="Get reconciliation audit logs",
    description="Get audit logs for a reconciliation."
)
async def get_reconciliation_audit_logs(
    reconciliation_id: UUID,
    action: Optional[str] = Query(None, description="Filter by action type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (greater than or equal)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (less than or equal)"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID who performed the action"),
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationAuditService = Depends(get_reconciliation_audit_service)
):
    try:
        logs, _ = service.list_audit_logs(
            reconciliation_id=reconciliation_id,
            user_id=current_user.id,
            action=action,
            start_date=start_date,
            end_date=end_date,
            user_filter=user_id
        )
        return logs
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/reconciliations/{reconciliation_id}/audit-logs/export",
    summary="Export reconciliation audit logs",
    description="Export reconciliation audit logs in the specified format (CSV, JSON, or XLSX)."
)
async def export_reconciliation_audit_logs(
    reconciliation_id: UUID,
    format: ReconciliationExportFormat = Query(ReconciliationExportFormat.CSV, description="Export format"),
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationAuditService = Depends(get_reconciliation_audit_service)
):
    try:
        if format == ReconciliationExportFormat.CSV:
            content = service.export_audit_logs(
                reconciliation_id=reconciliation_id,
                user_id=current_user.id,
                format="csv"
            )
            return Response(
                content=content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=reconciliation_audit_logs_{reconciliation_id}.csv"}
            )
        
        elif format == ReconciliationExportFormat.JSON:
            content = service.export_audit_logs(
                reconciliation_id=reconciliation_id,
                user_id=current_user.id,
                format="json"
            )
            return Response(
                content=content,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=reconciliation_audit_logs_{reconciliation_id}.json"}
            )
        
        elif format == ReconciliationExportFormat.XLSX:
            file_path = service.export_audit_logs(
                reconciliation_id=reconciliation_id,
                user_id=current_user.id,
                format="xlsx"
            )
            
            # Clean up the temporary file after sending the response
            response = FileResponse(
                path=file_path,
                filename=f"reconciliation_audit_logs_{reconciliation_id}.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Delete the temporary file after the response is sent
            response.headers["X-Accel-Buffering"] = "no"
            response.background = lambda: os.unlink(file_path)
            
            return response
    
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Reconciliation Matching Endpoints

@router.post(
    "/reconciliations/{reconciliation_id}/auto-match",
    response_model=List[ReconciliationItemSchema],
    summary="Auto-match reconciliation items",
    description="Automatically match reconciliation items based on defined rules."
)
async def auto_match_reconciliation_items(
    reconciliation_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        return service.auto_match_items(reconciliation_id, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/reconciliations/{reconciliation_id}/complete",
    response_model=ReconciliationSchema,
    summary="Complete a reconciliation",
    description="Mark a reconciliation as completed."
)
async def complete_reconciliation(
    reconciliation_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        return service.complete_reconciliation(reconciliation_id, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        if "not balanced" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/reconciliations/{reconciliation_id}/reopen",
    response_model=ReconciliationSchema,
    summary="Reopen a completed reconciliation",
    description="Reopen a completed reconciliation for further editing."
)
async def reopen_reconciliation(
    reconciliation_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
    service: ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        return service.reopen_reconciliation(reconciliation_id, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
