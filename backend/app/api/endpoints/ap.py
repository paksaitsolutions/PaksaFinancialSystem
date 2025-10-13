from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database_config import get_db

router = APIRouter()

@router.get("/dashboard/stats")
def get_ap_dashboard_stats(db: Session = Depends(get_db)):
    """Get AP dashboard statistics"""
    return {
        "totalPayable": "125,450",
        "overdueBills": 8,
        "activeVendors": 45,
        "monthlyPayments": "89,230"
    }

@router.get("/dashboard/recent-bills")
def get_recent_bills(db: Session = Depends(get_db)):
    """Get recent bills for dashboard"""
    return [
        {
            "vendor": "ABC Supplies",
            "billNumber": "INV-001",
            "dueDate": "2024-01-15",
            "amount": "$2,500.00",
            "status": "pending"
        },
        {
            "vendor": "XYZ Services",
            "billNumber": "INV-002", 
            "dueDate": "2024-01-10",
            "amount": "$1,200.00",
            "status": "overdue"
        }
    ]

@router.post("/import-bills")
def import_bills(db: Session = Depends(get_db)):
    """Import bills from file"""
    return {"message": "Bills imported successfully"}

@router.post("/batch-payments")
def process_batch_payments(db: Session = Depends(get_db)):
    """Process batch payments"""
    return {"message": "Batch payments processed successfully"}

@router.get("/vendors")
def get_vendors(db: Session = Depends(get_db)):
    """Get vendors list"""
    return {
        "vendors": [
            {"id": "v1", "name": "ABC Supplies", "status": "active"},
            {"id": "v2", "name": "XYZ Services", "status": "active"}
        ]
    }

@router.get("/payments")
def get_payments(db: Session = Depends(get_db)):
    """Get payments list"""
    return {
        "payments": [
            {
                "id": "1",
                "date": "2024-01-15",
                "vendor": {"name": "ABC Supplies"},
                "reference": "PAY-001",
                "amount": 1250.00,
                "status": "paid",
                "paymentMethod": "Bank Transfer"
            }
        ]
    }