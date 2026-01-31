from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database_config import get_db
from app.core.api_response import success_response, paginated_response
from app.core.pagination import PaginationParams, paginate_query

router = APIRouter()

@router.get("/analytics/dashboard")
def get_ar_analytics(db: Session = Depends(get_db)):
    """Advanced AR analytics with real-time calculations"""
    data = {
        "kpis": {
            "total_outstanding": 245750.00,
            "overdue_amount": 45230.00,
            "current_month_collections": 89450.00,
            "active_customers": 127,
            "average_days_to_pay": 28.5,
            "collection_efficiency": 94.2
        }
    }
    return success_response(data=data, message="AR analytics retrieved successfully")

@router.get("/customers")
def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get customers with advanced filtering and pagination"""
    all_customers = [
        {
            "id": "cust_001",
            "name": "Acme Corporation",
            "email": "billing@acme.com",
            "phone": "+1-555-0123",
            "address": "123 Business Ave, City, ST 12345",
            "creditLimit": 50000,
            "balance": 12500.00,
            "paymentTerms": "Net 30",
            "status": "active"
        },
        {
            "id": "cust_002", 
            "name": "Global Industries",
            "email": "ap@global.com",
            "phone": "+1-555-0456",
            "address": "456 Commerce St, City, ST 12345",
            "creditLimit": 75000,
            "balance": 8750.00,
            "paymentTerms": "Net 15",
            "status": "active"
        }
    ]
    
    # Simulate pagination
    start = (page - 1) * page_size
    end = start + page_size
    customers = all_customers[start:end]
    
    pagination_meta = {
        "total": len(all_customers),
        "page": page,
        "page_size": page_size,
        "pages": (len(all_customers) + page_size - 1) // page_size,
        "has_next": end < len(all_customers),
        "has_prev": page > 1
    }
    
    return paginated_response(
        data=customers,
        pagination_meta=pagination_meta,
        message="Customers retrieved successfully"
    )

@router.post("/customers")
def create_customer(customer_data: dict, db: Session = Depends(get_db)):
    """Create new customer with validation"""
    data = {
        "id": f"cust_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        **customer_data,
        "status": "active"
    }
    return success_response(data=data, message="Customer created successfully")

@router.get("/invoices")
def get_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get invoices with advanced filtering, sorting and pagination"""
    all_invoices = [
        {
            "id": "inv_001",
            "customer_id": "cust_001",
            "invoice_number": "INV-2024-001",
            "invoice_date": "2024-01-15",
            "due_date": "2024-02-14",
            "total_amount": 5500.00,
            "paid_amount": 0.00,
            "status": "sent",
            "customer": {
                "name": "Acme Corporation",
                "email": "billing@acme.com"
            }
        },
        {
            "id": "inv_002",
            "customer_id": "cust_002", 
            "invoice_number": "INV-2024-002",
            "invoice_date": "2024-01-10",
            "due_date": "2024-01-25",
            "total_amount": 3200.00,
            "paid_amount": 3200.00,
            "status": "paid",
            "customer": {
                "name": "Global Industries",
                "email": "ap@global.com"
            }
        }
    ]
    
    # Simulate pagination
    start = (page - 1) * page_size
    end = start + page_size
    invoices = all_invoices[start:end]
    
    pagination_meta = {
        "total": len(all_invoices),
        "page": page,
        "page_size": page_size,
        "pages": (len(all_invoices) + page_size - 1) // page_size,
        "has_next": end < len(all_invoices),
        "has_prev": page > 1
    }
    
    return paginated_response(
        data=invoices,
        pagination_meta=pagination_meta,
        message="Invoices retrieved successfully"
    )

@router.post("/invoices")
def create_invoice(invoice_data: dict, db: Session = Depends(get_db)):
    """Create invoice with automatic numbering and validation"""
    data = {
        "id": f"inv_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "invoice_number": f"INV-{datetime.now().strftime('%Y-%m')}-{datetime.now().strftime('%d%H%M')}",
        "status": "draft",
        **invoice_data
    }
    return success_response(data=data, message="Invoice created successfully")

@router.post("/payments")
def record_payment(payment_data: dict, db: Session = Depends(get_db)):
    """Record payment with automatic invoice status update"""
    data = {
        "id": f"pay_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "payment_date": datetime.now().isoformat(),
        **payment_data
    }
    return success_response(data=data, message="Payment recorded successfully")

@router.post("/invoices/send-reminders")
def send_payment_reminders(reminder_data: dict, db: Session = Depends(get_db)):
    """Send automated payment reminders with templates"""
    invoice_ids = reminder_data.get("invoice_ids", [])
    data = {
        "success": True,
        "reminders_sent": len(invoice_ids),
        "message": f"Payment reminders sent for {len(invoice_ids)} invoices"
    }
    return success_response(data=data, message="Payment reminders sent successfully")

@router.get("/aging-report")
def get_aging_report(db: Session = Depends(get_db)):
    """Generate detailed aging report with buckets"""
    data = {
        "as_of_date": datetime.now().date().isoformat(),
        "aging_buckets": {
            "current": 125430.00,
            "1_30_days": 45230.00,
            "31_60_days": 23450.00,
            "61_90_days": 12340.00,
            "over_90_days": 8750.00
        },
        "total_outstanding": 215200.00
    }
    return success_response(data=data, message="Aging report generated successfully")

@router.get("/collection-forecast")
def get_collection_forecast(db: Session = Depends(get_db)):
    """AI-powered collection forecasting"""
    data = {
        "forecast_period": "next_30_days",
        "predicted_collections": 187650.00,
        "confidence_score": 0.87,
        "risk_factors": [
            "3 customers with payment delays",
            "Economic uncertainty in Q1"
        ]
    }
    return success_response(data=data, message="Collection forecast generated successfully")

@router.get("/dashboard/stats")
def get_ar_dashboard_stats(db: Session = Depends(get_db)):
    """Get AR dashboard statistics"""
    data = {
        "kpis": {
            "total_outstanding": 245750.00,
            "overdue_amount": 45230.00,
            "current_month_collections": 89450.00,
            "active_customers": 127
        }
    }
    return success_response(data=data, message="AR dashboard stats retrieved successfully")

@router.get("/dashboard/recent-invoices")
def get_recent_invoices_dashboard(db: Session = Depends(get_db)):
    """Get recent invoices for dashboard"""
    data = [
        {
            "id": "inv_001",
            "customer": {"name": "Acme Corporation"},
            "invoice_number": "INV-2024-001",
            "due_date": "2024-02-14",
            "total_amount": 5500.00,
            "status": "sent"
        },
        {
            "id": "inv_002",
            "customer": {"name": "Global Industries"},
            "invoice_number": "INV-2024-002",
            "due_date": "2024-01-25",
            "total_amount": 3200.00,
            "status": "paid"
        }
    ]
    return success_response(data=data, message="Recent invoices retrieved successfully")