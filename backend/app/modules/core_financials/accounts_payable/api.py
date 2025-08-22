from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.db import get_db

# Import services with string literals to avoid circular imports
from .services.vendor_service import VendorService
from .services.invoice_service import InvoiceService
from .services.payment_service import PaymentService
from .services.analytics_service import APAnalyticsService

router = APIRouter(prefix="/ap", tags=["Accounts Payable"])

# Vendor Management API
@router.post("/vendors/", response_model=dict)
async def create_vendor(
    vendor: dict,
    db: Session = Depends(get_db)
):
    """Create a new vendor"""
    vendor_service = VendorService(db)
    from app.modules.core_financials.accounts_payable.schemas import VendorCreate
    vendor_data = VendorCreate(**vendor)
    result = vendor_service.create_vendor(vendor_data)
    return {"id": result.id, "vendor_id": result.vendor_id, "name": result.name}

@router.get("/vendors/", response_model=List[dict])
async def get_vendors(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of vendors with optional filtering"""
    vendor_service = VendorService(db)
    vendors = vendor_service.get_vendors(skip=skip, limit=limit, search=search, status=status, category=category)
    return [{"id": v.id, "vendor_id": v.vendor_id, "name": v.name, "category": v.category.value, "status": v.status.value, "outstanding_balance": float(v.outstanding_balance)} for v in vendors]

@router.get("/vendors/{vendor_id}", response_model=dict)
async def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    """Get vendor by ID"""
    vendor_service = VendorService(db)
    vendor = vendor_service.get_vendor(vendor_id)
    return {"id": vendor.id, "vendor_id": vendor.vendor_id, "name": vendor.name, "category": vendor.category.value, "status": vendor.status.value}

@router.put("/vendors/{vendor_id}", response_model=dict)
async def update_vendor(
    vendor_id: int,
    vendor: dict,
    db: Session = Depends(get_db)
):
    """Update vendor"""
    vendor_service = VendorService(db)
    from app.modules.core_financials.accounts_payable.schemas import VendorUpdate
    vendor_data = VendorUpdate(**vendor)
    result = vendor_service.update_vendor(vendor_id, vendor_data)
    return {"id": result.id, "vendor_id": result.vendor_id, "name": result.name}

@router.delete("/vendors/{vendor_id}")
async def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    """Delete vendor"""
    vendor_service = VendorService(db)
    vendor_service.delete_vendor(vendor_id)
    return {"message": "Vendor deleted successfully"}

# Invoice Management API
@router.post("/invoices/", response_model=dict)
async def create_invoice(
    invoice: dict,
    db: Session = Depends(get_db)
):
    """Create a new invoice"""
    invoice_service = InvoiceService(db)
    from app.modules.core_financials.accounts_payable.schemas import InvoiceCreate
    invoice_data = InvoiceCreate(**invoice)
    result = invoice_service.create_invoice(invoice_data)
    return {"id": result.id, "invoice_number": result.invoice_number, "total_amount": float(result.total_amount)}

@router.get("/invoices/", response_model=List[dict])
async def get_invoices(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of invoices with optional filtering"""
    invoice_service = InvoiceService(db)
    invoices = invoice_service.get_invoices(skip=skip, limit=limit, search=search, status=status, vendor_id=vendor_id)
    return [{"id": i.id, "invoice_number": i.invoice_number, "vendor_name": i.vendor_name, "total_amount": float(i.total_amount), "status": i.status.value} for i in invoices]

@router.get("/invoices/{invoice_id}", response_model=dict)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Get invoice by ID"""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice(invoice_id)
    return {"id": invoice.id, "invoice_number": invoice.invoice_number, "total_amount": float(invoice.total_amount)}

@router.post("/invoices/{invoice_id}/approve", response_model=dict)
async def approve_invoice(
    invoice_id: int,
    approved_by: str,
    db: Session = Depends(get_db)
):
    """Approve invoice"""
    invoice_service = InvoiceService(db)
    result = invoice_service.approve_invoice(invoice_id, approved_by)
    return {"id": result.id, "status": result.status.value}

# Payment Management API
@router.post("/payments/", response_model=dict)
async def create_payment(
    payment: dict,
    db: Session = Depends(get_db)
):
    """Create a new payment"""
    payment_service = PaymentService(db)
    from app.modules.core_financials.accounts_payable.schemas import PaymentCreate
    payment_data = PaymentCreate(**payment)
    result = payment_service.create_payment(payment_data)
    return {"id": result.id, "payment_number": result.payment_number, "amount": float(result.amount)}

@router.get("/payments/", response_model=List[dict])
async def get_payments(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of payments with optional filtering"""
    payment_service = PaymentService(db)
    payments = payment_service.get_payments(skip=skip, limit=limit, search=search, status=status, vendor_id=vendor_id)
    return [{"id": p.id, "payment_number": p.payment_number, "vendor_name": p.vendor_name, "amount": float(p.amount), "status": p.status.value} for p in payments]

@router.post("/payments/{payment_id}/process", response_model=dict)
async def process_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Process payment"""
    payment_service = PaymentService(db)
    result = payment_service.process_payment(payment_id)
    return {"id": result.id, "status": result.status.value}

# Analytics and Reporting
@router.get("/analytics/summary", response_model=dict)
async def get_ap_summary(
    db: Session = Depends(get_db)
):
    """Get AP summary analytics"""
    analytics_service = APAnalyticsService(db)
    summary = analytics_service.get_ap_summary()
    return {
        "total_outstanding": float(summary.total_outstanding),
        "overdue_amount": float(summary.overdue_amount),
        "this_month_invoices": float(summary.this_month_invoices),
        "pending_approval": float(summary.pending_approval),
        "total_vendors": summary.total_vendors,
        "active_vendors": summary.active_vendors
    }

@router.get("/analytics/aging-report", response_model=dict)
async def get_aging_report(
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get accounts payable aging report"""
    analytics_service = APAnalyticsService(db)
    report = analytics_service.get_aging_report(as_of_date)
    return {
        "report_date": report.report_date.isoformat(),
        "items": [{"vendor_name": item.vendor_name, "total_outstanding": float(item.total_outstanding)} for item in report.items],
        "totals": {"total_outstanding": float(report.totals.total_outstanding)}
    }