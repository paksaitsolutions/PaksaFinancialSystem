from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from ..services.customer_service import CustomerService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new customer with real database persistence"""
    customer_service = CustomerService()
    customer = await customer_service.create_customer(db, customer_data, current_user.id)
    return {"message": "Customer created successfully", "data": customer}

@router.get("/")
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    customer_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all customers with real database filtering"""
    customer_service = CustomerService()
    customers = await customer_service.get_customers(db, skip, limit, status, customer_type)
    return {"customers": customers, "total": len(customers)}

@router.get("/{customer_id}")
async def get_customer(
    customer_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer by ID with complete details"""
    customer_service = CustomerService()
    customer = await customer_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}")
async def update_customer(
    customer_id: int, 
    customer_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customer with real database persistence"""
    customer_service = CustomerService()
    customer = await customer_service.update_customer(db, customer_id, customer_data, current_user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer updated successfully", "data": customer}

@router.get("/{customer_id}/aging")
async def get_customer_aging(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer aging analysis from real data"""
    customer_service = CustomerService()
    aging = await customer_service.get_customer_aging_analysis(db, customer_id)
    return {"aging_analysis": aging}

@router.post("/{customer_id}/credit-limit")
async def update_credit_limit(
    customer_id: int,
    credit_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customer credit limit with validation"""
    customer_service = CustomerService()
    result = await customer_service.update_credit_limit(db, customer_id, credit_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Credit limit updated successfully", "data": result}

@router.post("/{customer_id}/credit-hold")
async def manage_credit_hold(
    customer_id: int,
    hold_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Place or remove credit hold on customer"""
    customer_service = CustomerService()
    result = await customer_service.place_credit_hold(db, customer_id, hold_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Credit hold updated successfully", "data": result}

@router.get("/{customer_id}/payment-history")
async def get_payment_history(
    customer_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer payment history"""
    customer_service = CustomerService()
    history = await customer_service.get_customer_payment_history(db, customer_id, limit)
    return {"payment_history": history}

@router.get("/aging/all")
async def get_all_customer_aging(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aging analysis for all customers"""
    customer_service = CustomerService()
    aging = await customer_service.get_customer_aging_analysis(db)
    return {"aging_analysis": aging}
