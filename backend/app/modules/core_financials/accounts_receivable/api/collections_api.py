from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from ..services.collections_service import CollectionsService

router = APIRouter()

@router.get("/dashboard")
async def get_collections_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get collections dashboard data"""
    collections_service = CollectionsService()
    dashboard = await collections_service.get_collections_dashboard(db)
    return dashboard

@router.get("/overdue")
async def get_overdue_invoices(
    days_overdue: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overdue invoices for collections"""
    collections_service = CollectionsService()
    overdue = await collections_service.get_overdue_invoices(db, days_overdue)
    return {"overdue_invoices": overdue}

@router.post("/activities", status_code=status.HTTP_201_CREATED)
async def create_collection_activity(
    activity_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a collection activity record"""
    collections_service = CollectionsService()
    activity = await collections_service.create_collection_activity(db, activity_data, current_user.id)
    return {"message": "Collection activity created successfully", "data": activity}

@router.get("/activities")
async def get_collection_activities(
    customer_id: Optional[int] = None,
    invoice_id: Optional[int] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get collection activities with filtering"""
    collections_service = CollectionsService()
    activities = await collections_service.get_collection_activities(db, customer_id, invoice_id, limit)
    return {"activities": activities}

@router.post("/dunning-letters")
async def send_dunning_letter(
    dunning_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send dunning letter to customer"""
    collections_service = CollectionsService()
    result = await collections_service.send_dunning_letter(db, dunning_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "Dunning letter sent successfully", "data": result}

@router.post("/payment-reminders")
async def setup_payment_reminder(
    reminder_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set up automated payment reminder"""
    collections_service = CollectionsService()
    result = await collections_service.setup_payment_reminder(db, reminder_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Payment reminder setup successfully", "data": result}

@router.get("/follow-up-tasks")
async def get_follow_up_tasks(
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get collection follow-up tasks"""
    collections_service = CollectionsService()
    # If no user_id specified, get tasks for current user
    target_user_id = user_id if user_id else current_user.id
    tasks = await collections_service.get_follow_up_tasks(db, target_user_id)
    return {"follow_up_tasks": tasks}