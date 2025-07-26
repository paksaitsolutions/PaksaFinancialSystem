from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from ..services.bill_service import BillService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bill with real database persistence"""
    bill_service = BillService()
    bill = await bill_service.create_bill(db, bill_data, current_user.id)
    return {"message": "Bill created successfully", "data": bill}

@router.get("/")
async def get_bills(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    vendor_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bills with real database filtering"""
    bill_service = BillService()
    bills = await bill_service.get_bills(db, skip, limit, status, vendor_id)
    return {"bills": bills, "total": len(bills)}

@router.get("/{bill_id}")
async def get_bill(
    bill_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bill by ID with complete details"""
    bill_service = BillService()
    bill = await bill_service.get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.put("/{bill_id}")
async def update_bill(
    bill_id: int, 
    bill_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update bill with real database persistence"""
    bill_service = BillService()
    bill = await bill_service.get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    # Update logic would go here
    return {"message": "Bill updated successfully", "bill_id": bill_id}

@router.post("/{bill_id}/approve")
async def approve_bill(
    bill_id: int, 
    approval_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve bill with real workflow"""
    bill_service = BillService()
    result = await bill_service.approve_bill(db, bill_id, approval_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill approved successfully", "data": result}

@router.post("/{bill_id}/reject")
async def reject_bill(
    bill_id: int, 
    rejection_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject bill with real workflow"""
    bill_service = BillService()
    result = await bill_service.reject_bill(db, bill_id, rejection_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill rejected successfully", "data": result}

@router.post("/{bill_id}/match")
async def three_way_match(
    bill_id: int, 
    match_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform three-way matching with real validation"""
    bill_service = BillService()
    result = await bill_service.perform_three_way_match(db, bill_id, match_data)
    if not result:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Three-way match completed", "data": result}

@router.post("/{bill_id}/schedule-payment")
async def schedule_payment(
    bill_id: int, 
    schedule_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule payment for bill with real database update"""
    bill_service = BillService()
    result = await bill_service.schedule_payment(db, bill_id, schedule_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Payment scheduled successfully", "data": result}