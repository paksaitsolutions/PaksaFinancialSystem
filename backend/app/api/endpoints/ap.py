from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database_config import get_db
from app.core.api_response import success_response, paginated_response
from app.core.pagination import PaginationParams, paginate_query

router = APIRouter()

@router.get("/dashboard/stats")
def get_ap_dashboard_stats(db: Session = Depends(get_db)):
    """Get AP dashboard statistics"""
    data = {
        "totalPayable": "125,450",
        "overdueBills": 8,
        "activeVendors": 45,
        "monthlyPayments": "89,230"
    }
    return success_response(data=data, message="AP dashboard stats retrieved successfully")

@router.get("/dashboard/recent-bills")
def get_recent_bills(db: Session = Depends(get_db)):
    """Get recent bills for dashboard"""
    data = [
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
    return success_response(data=data, message="Recent bills retrieved successfully")

@router.post("/import-bills")
def import_bills(db: Session = Depends(get_db)):
    """Import bills from file"""
    return success_response(message="Bills imported successfully")

@router.post("/batch-payments")
def process_batch_payments(db: Session = Depends(get_db)):
    """Process batch payments"""
    return success_response(message="Batch payments processed successfully")

@router.get("/vendors")
def get_vendors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get vendors list with pagination"""
    # Mock data - replace with actual database query
    all_vendors = [
        {"id": "v1", "name": "ABC Supplies", "status": "active"},
        {"id": "v2", "name": "XYZ Services", "status": "active"}
    ]
    
    # Simulate pagination
    start = (page - 1) * page_size
    end = start + page_size
    vendors = all_vendors[start:end]
    
    pagination_meta = {
        "total": len(all_vendors),
        "page": page,
        "page_size": page_size,
        "pages": (len(all_vendors) + page_size - 1) // page_size,
        "has_next": end < len(all_vendors),
        "has_prev": page > 1
    }
    
    return paginated_response(
        data=vendors,
        pagination_meta=pagination_meta,
        message="Vendors retrieved successfully"
    )

@router.get("/payments")
def get_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get payments list with pagination"""
    # Mock data - replace with actual database query
    all_payments = [
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
    
    # Simulate pagination
    start = (page - 1) * page_size
    end = start + page_size
    payments = all_payments[start:end]
    
    pagination_meta = {
        "total": len(all_payments),
        "page": page,
        "page_size": page_size,
        "pages": (len(all_payments) + page_size - 1) // page_size,
        "has_next": end < len(all_payments),
        "has_prev": page > 1
    }
    
    return paginated_response(
        data=payments,
        pagination_meta=pagination_meta,
        message="Payments retrieved successfully"
    )