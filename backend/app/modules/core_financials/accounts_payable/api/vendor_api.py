from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from ..services.vendor_service import VendorService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new vendor with real database persistence"""
    vendor_service = VendorService()
    vendor = await vendor_service.create_vendor(db, vendor_data, current_user.id)
    return {"message": "Vendor created successfully", "data": vendor}

@router.get("/")
async def get_vendors(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all vendors with real database filtering"""
    vendor_service = VendorService()
    vendors = await vendor_service.get_vendors(db, skip, limit, status, category)
    return {"vendors": vendors, "total": len(vendors)}

@router.get("/{vendor_id}")
async def get_vendor(
    vendor_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vendor by ID with complete details"""
    vendor_service = VendorService()
    vendor = await vendor_service.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@router.put("/{vendor_id}")
async def update_vendor(
    vendor_id: int, 
    vendor_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update vendor with real database persistence"""
    vendor_service = VendorService()
    vendor = await vendor_service.update_vendor(db, vendor_id, vendor_data, current_user.id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor updated successfully", "data": vendor}

@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete vendor with validation"""
    vendor_service = VendorService()
    result = await vendor_service.delete_vendor(db, vendor_id)
    if not result["deleted"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "Vendor deleted successfully"}

@router.post("/{vendor_id}/approve")
async def approve_vendor(
    vendor_id: int, 
    approval_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve vendor with real workflow"""
    vendor_service = VendorService()
    result = await vendor_service.approve_vendor(db, vendor_id, approval_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor approved successfully", "data": result}

@router.post("/{vendor_id}/reject")
async def reject_vendor(
    vendor_id: int, 
    rejection_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject vendor with real workflow"""
    vendor_service = VendorService()
    result = await vendor_service.reject_vendor(db, vendor_id, rejection_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor rejected successfully", "data": result}

@router.get("/{vendor_id}/performance")
async def get_vendor_performance(
    vendor_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vendor performance metrics from real data"""
    vendor_service = VendorService()
    performance = await vendor_service.get_vendor_performance(db, vendor_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return performance

@router.post("/{vendor_id}/evaluation")
async def create_vendor_evaluation(
    vendor_id: int, 
    evaluation_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create vendor evaluation with real database persistence"""
    vendor_service = VendorService()
    evaluation = await vendor_service.create_evaluation(db, vendor_id, evaluation_data, current_user.id)
    return {"message": "Evaluation created successfully", "data": evaluation}
