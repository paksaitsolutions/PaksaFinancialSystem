from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db.database import get_db

router = APIRouter()

@router.get("/workflow")
async def get_collections_workflow(db: AsyncSession = Depends(get_db)):
    """Get collections workflow status"""
    return {
        "total_overdue": 125000.00,
        "customers_in_collections": 25,
        "workflow_stages": [
            {"stage": "30_days", "count": 15, "amount": 45000.00},
            {"stage": "60_days", "count": 8, "amount": 35000.00},
            {"stage": "90_days", "count": 2, "amount": 45000.00}
        ]
    }

@router.post("/workflow/{customer_id}")
async def start_collections_workflow(customer_id: int, workflow_data: dict, db: AsyncSession = Depends(get_db)):
    """Start collections workflow for customer"""
    return {
        "customer_id": customer_id,
        "workflow_id": 1,
        "status": "started",
        "next_action": "send_reminder"
    }

@router.get("/dunning-letters")
async def get_dunning_letters(db: AsyncSession = Depends(get_db)):
    """Get dunning letter templates"""
    return {
        "templates": [
            {"id": 1, "name": "First Notice", "days_overdue": 30},
            {"id": 2, "name": "Second Notice", "days_overdue": 60},
            {"id": 3, "name": "Final Notice", "days_overdue": 90}
        ]
    }

@router.post("/dunning-letters/send")
async def send_dunning_letter(letter_data: dict, db: AsyncSession = Depends(get_db)):
    """Send dunning letter to customer"""
    return {
        "customer_id": letter_data.get("customer_id"),
        "template_id": letter_data.get("template_id"),
        "sent_date": "2024-01-15",
        "status": "sent"
    }

@router.get("/reminders")
async def get_payment_reminders(db: AsyncSession = Depends(get_db)):
    """Get payment reminders"""
    return {"reminders": []}

@router.post("/reminders")
async def create_payment_reminder(reminder_data: dict, db: AsyncSession = Depends(get_db)):
    """Create payment reminder"""
    return {
        "reminder_id": 1,
        "customer_id": reminder_data.get("customer_id"),
        "reminder_date": reminder_data.get("date"),
        "type": reminder_data.get("type"),
        "status": "scheduled"
    }

@router.post("/reminders/{reminder_id}/send")
async def send_payment_reminder(reminder_id: int, db: AsyncSession = Depends(get_db)):
    """Send payment reminder"""
    return {
        "reminder_id": reminder_id,
        "sent_date": "2024-01-15",
        "status": "sent"
    }

@router.get("/aging-report")
async def get_aging_report(db: AsyncSession = Depends(get_db)):
    """Get accounts receivable aging report"""
    return {
        "report_date": "2024-01-15",
        "total_outstanding": 250000.00,
        "aging_buckets": {
            "current": 150000.00,
            "days_30": 50000.00,
            "days_60": 30000.00,
            "days_90": 15000.00,
            "over_90": 5000.00
        },
        "customers": []
    }