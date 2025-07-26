from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from ..services.payment_service import PaymentService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment with real database persistence"""
    payment_service = PaymentService()
    payment = await payment_service.create_payment(db, payment_data, current_user.id)
    return {"message": "Payment created successfully", "data": payment}

@router.get("/")
async def get_payments(
    skip: int = 0,
    limit: int = 100,
    vendor_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments with real database filtering"""
    payment_service = PaymentService()
    payments = await payment_service.get_payments(db, skip, limit, vendor_id, status)
    return {"payments": payments, "total": len(payments)}

@router.get("/{payment_id}")
async def get_payment(
    payment_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment by ID with complete details"""
    payment_service = PaymentService()
    payment = await payment_service.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/batch")
async def process_payment_batch(
    batch_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process multiple payments in a batch"""
    payment_service = PaymentService()
    result = await payment_service.process_payment_batch(db, batch_data, current_user.id)
    return {"message": "Payment batch processed", "data": result}

@router.post("/{payment_id}/approve")
async def approve_payment(
    payment_id: int, 
    approval_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve payment with real workflow"""
    payment_service = PaymentService()
    result = await payment_service.approve_payment(db, payment_id, approval_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment approved successfully", "data": result}

@router.post("/{payment_id}/void")
async def void_payment(
    payment_id: int, 
    void_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Void payment and reverse invoice applications"""
    payment_service = PaymentService()
    result = await payment_service.void_payment(db, payment_id, void_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment voided successfully", "data": result}

@router.get("/methods")
async def get_payment_methods(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available payment methods"""
    payment_service = PaymentService()
    methods = await payment_service.get_payment_methods(db)
    return {"payment_methods": methods}

@router.get("/vendor/{vendor_id}/history")
async def get_payment_history(
    vendor_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment history for a vendor"""
    payment_service = PaymentService()
    history = await payment_service.get_payment_history(db, vendor_id, limit)
    return {"payment_history": history}