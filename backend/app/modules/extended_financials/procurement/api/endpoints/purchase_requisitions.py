from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from ..extended_financials.procurement.schemas.purchase_requisition import (
    PurchaseRequisitionCreate,
    PurchaseRequisitionUpdate,
    PurchaseRequisitionResponse,
    PurchaseRequisitionList,
    RequisitionApproval,
    RequisitionFilter
)
from ..extended_financials.procurement.services.purchase_requisition_service import PurchaseRequisitionService
from app.core.logging import logger

router = APIRouter()

@router.post(
    "/",
    response_model=PurchaseRequisitionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new purchase requisition",
    description="Create a new purchase requisition with line items."
)
async def create_requisition(
    requisition: PurchaseRequisitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new purchase requisition.
    
    - **title**: Title of the requisition
    - **description**: Detailed description (optional)
    - **items**: List of items being requested (at least one required)
    - **department_id**: Department ID for the requisition (optional)
    - **priority**: Priority level (low, medium, high, urgent)
    - **required_date**: When the items are needed by (optional)
    """
    service = PurchaseRequisitionService(db, current_user)
    return service.create_requisition(requisition)

@router.get(
    "/{requisition_id}",
    response_model=PurchaseRequisitionResponse,
    summary="Get a purchase requisition by ID",
    description="Retrieve details of a specific purchase requisition."
)
async def get_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific purchase requisition by its ID.
    
    - **requisition_id**: The ID of the requisition to retrieve
    """
    service = PurchaseRequisitionService(db, current_user)
    return service.get_requisition(requisition_id)

@router.get(
    "/",
    response_model=List[PurchaseRequisitionList],
    summary="List purchase requisitions",
    description="List all purchase requisitions with optional filtering and pagination."
)
async def list_requisitions(
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Maximum number of items to return"),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    requester_id: Optional[int] = None,
    department_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all purchase requisitions with optional filtering.
    
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return (for pagination)
    - **status**: Filter by status (draft, submitted, approved, rejected, converted_to_po)
    - **priority**: Filter by priority (low, medium, high, urgent)
    - **requester_id**: Filter by requester ID
    - **department_id**: Filter by department ID
    - **start_date**: Filter by requisition date (greater than or equal to)
    - **end_date**: Filter by requisition date (less than or equal to)
    - **search**: Search term to filter by title, description, or requisition number
    """
    # Parse dates if provided
    from datetime import datetime
    
    filters = RequisitionFilter(
        status=status,
        priority=priority,
        requester_id=requester_id,
        department_id=department_id,
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None,
        search=search
    )
    
    service = PurchaseRequisitionService(db, current_user)
    return service.list_requisitions(skip, limit, filters)

@router.put(
    "/{requisition_id}",
    response_model=PurchaseRequisitionResponse,
    summary="Update a purchase requisition",
    description="Update an existing purchase requisition."
)
async def update_requisition(
    requisition_id: int,
    requisition: PurchaseRequisitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing purchase requisition.
    
    - **requisition_id**: The ID of the requisition to update
    - **requisition**: The updated requisition data
    """
    service = PurchaseRequisitionService(db, current_user)
    return service.update_requisition(requisition_id, requisition)

@router.post(
    "/{requisition_id}/submit",
    response_model=PurchaseRequisitionResponse,
    summary="Submit a requisition for approval",
    description="Submit a draft requisition for approval."
)
async def submit_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a draft requisition for approval.
    
    - **requisition_id**: The ID of the requisition to submit
    """
    service = PurchaseRequisitionService(db, current_user)
    return service.submit_requisition(requisition_id)

@router.post(
    "/{requisition_id}/approve",
    response_model=PurchaseRequisitionResponse,
    summary="Approve or reject a requisition",
    description="Approve or reject a submitted purchase requisition."
)
async def approve_requisition(
    requisition_id: int,
    approval: RequisitionApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Approve or reject a submitted purchase requisition.
    
    - **requisition_id**: The ID of the requisition to approve/reject
    - **approved**: Boolean indicating approval (true) or rejection (false)
    - **notes**: Optional notes about the approval/rejection
    """
    service = PurchaseRequisitionService(db, current_user)
    return service.approve_requisition(requisition_id, approval)

@router.delete(
    "/{requisition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a purchase requisition",
    description="Delete a draft purchase requisition."
)
async def delete_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a draft purchase requisition.
    
    - **requisition_id**: The ID of the requisition to delete
    """
    service = PurchaseRequisitionService(db, current_user)
    if service.delete_requisition(requisition_id):
        return None
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete purchase requisition"
    )

# Additional endpoints for reporting and analytics
@router.get(
    "/reports/summary",
    summary="Get requisition summary report",
    description="Get a summary report of purchase requisitions by status, department, etc."
)
async def get_requisition_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a summary report of purchase requisitions.
    
    - **start_date**: Start date for the report (YYYY-MM-DD)
    - **end_date**: End date for the report (YYYY-MM-DD)
    - **department_id**: Filter by department ID (optional)
    """
    # This is a placeholder - implement actual reporting logic
    from datetime import datetime, timedelta
    
    # Default to last 30 days if no date range provided
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    
    # TODO: Implement actual reporting logic
    return {
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "summary": {
            "total_requisitions": 0,
            "total_amount": 0,
            "by_status": {},
            "by_department": {},
            "by_category": {}
        }
    }
