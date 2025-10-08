"""
Main Accounts Receivable API router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.crud.accounts_receivable.customer import CustomerCRUD
from app.crud.accounts_receivable.ar_invoice import ARInvoiceCRUD
from app.crud.accounts_receivable.ar_payment import ARPaymentCRUD

router = APIRouter()

# Customers endpoints
@router.get("/customers", response_model=dict)
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all customers with filtering"""
    customer_crud = CustomerCRUD()
    customers = await customer_crud.get_customers(db, skip=skip, limit=limit, status=status, search=search)
    total = await customer_crud.count_customers(db, status=status, search=search)
    
    return {
        "customers": customers,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/customers/{customer_id}")
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer by ID"""
    customer_crud = CustomerCRUD()
    customer = await customer_crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Invoices endpoints
@router.get("/invoices", response_model=dict)
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    overdue_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all invoices with filtering"""
    invoice_crud = ARInvoiceCRUD()
    invoices = await invoice_crud.get_invoices(
        db, skip=skip, limit=limit, status=status, 
        customer_id=customer_id, overdue_only=overdue_only
    )
    total = await invoice_crud.count_invoices(
        db, status=status, customer_id=customer_id, overdue_only=overdue_only
    )
    
    return {
        "invoices": invoices,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice by ID"""
    invoice_crud = ARInvoiceCRUD()
    invoice = await invoice_crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

# Payments endpoints
@router.get("/payments", response_model=dict)
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments with filtering"""
    payment_crud = ARPaymentCRUD()
    payments = await payment_crud.get_payments(db, skip=skip, limit=limit, status=status, customer_id=customer_id)
    total = await payment_crud.count_payments(db, status=status, customer_id=customer_id)
    
    return {
        "payments": payments,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# Analytics endpoints
@router.get("/analytics/dashboard")
async def get_dashboard_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AR dashboard analytics"""
    invoice_crud = ARInvoiceCRUD()
    customer_crud = CustomerCRUD()
    
    # Calculate key metrics
    total_outstanding = await invoice_crud.get_total_outstanding(db)
    overdue_amount = await invoice_crud.get_overdue_amount(db)
    current_month_collections = await invoice_crud.get_current_month_collections(db)
    dso = await invoice_crud.calculate_dso(db)
    
    # Customer metrics
    total_customers = await customer_crud.count_customers(db)
    active_customers = await customer_crud.count_customers(db, status="active")
    
    return {
        "kpis": {
            "total_outstanding": float(total_outstanding or 0),
            "overdue_amount": float(overdue_amount or 0),
            "current_month_collections": float(current_month_collections or 0),
            "dso": float(dso or 0),
            "total_customers": total_customers,
            "active_customers": active_customers
        },
        "aging_buckets": await invoice_crud.get_aging_analysis(db),
        "collection_metrics": await invoice_crud.get_collection_effectiveness(db),
        "payment_forecasts": await generate_payment_forecasts(db),
        "risk_analysis": await generate_risk_analysis(db)
    }

@router.get("/analytics/aging-report")
async def get_aging_report(
    as_of_date: Optional[date] = None,
    customer_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AR aging report"""
    invoice_crud = ARInvoiceCRUD()
    aging_data = await invoice_crud.get_detailed_aging_report(db, as_of_date, customer_id)
    
    return {
        "aging_buckets": aging_data,
        "summary": {
            "total_current": sum(bucket.get("current", 0) for bucket in aging_data),
            "total_1_30": sum(bucket.get("days_1_30", 0) for bucket in aging_data),
            "total_31_60": sum(bucket.get("days_31_60", 0) for bucket in aging_data),
            "total_60_plus": sum(bucket.get("days_60_plus", 0) for bucket in aging_data),
        }
    }

@router.get("/analytics/collection-forecast")
async def get_collection_forecast(
    days: int = Query(90, ge=30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get collection forecast"""
    forecasts = await generate_payment_forecasts(db, days)
    return {
        "forecasts": forecasts,
        "confidence_level": 85,
        "total_forecast": sum(f["amount"] for f in forecasts)
    }

@router.get("/analytics/customer-segmentation")
async def get_customer_segmentation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer segmentation analysis"""
    customer_crud = CustomerCRUD()
    segments = await customer_crud.get_customer_segmentation(db)
    
    return {
        "segments": segments,
        "total_customers": sum(s["count"] for s in segments),
        "total_value": sum(s["value"] for s in segments)
    }

# Helper functions
async def generate_payment_forecasts(db: AsyncSession, days: int = 30):
    """Generate payment forecasts"""
    # Mock forecast data - replace with actual ML predictions
    today = date.today()
    forecasts = []
    
    for week in range(1, min(days // 7, 13) + 1):
        week_start = today + timedelta(days=(week-1)*7)
        week_end = week_start + timedelta(days=6)
        
        # Mock forecast calculation
        base_amount = 125000 - (week * 5000)  # Decreasing trend
        confidence = max(95 - (week * 5), 60)  # Decreasing confidence
        
        forecasts.append({
            "period": f"Week {week}",
            "start_date": week_start.isoformat(),
            "end_date": week_end.isoformat(),
            "amount": base_amount,
            "confidence": confidence,
            "risk_level": "low" if confidence > 80 else "medium" if confidence > 65 else "high"
        })
    
    return forecasts

async def generate_risk_analysis(db: AsyncSession):
    """Generate customer risk analysis"""
    # Mock risk analysis - replace with actual ML model
    return {
        "high_risk_customers": 5,
        "medium_risk_customers": 12,
        "low_risk_customers": 156,
        "total_at_risk_amount": 285000,
        "risk_factors": [
            {"factor": "Payment History", "weight": 0.4},
            {"factor": "Days Past Due", "weight": 0.3},
            {"factor": "Credit Utilization", "weight": 0.2},
            {"factor": "Industry Risk", "weight": 0.1}
        ]
    }