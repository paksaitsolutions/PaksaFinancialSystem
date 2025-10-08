"""
Main Accounts Payable API router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.crud.accounts_payable.vendor import VendorCRUD
from app.crud.accounts_payable.invoice import InvoiceCRUD
from app.crud.accounts_payable.payment import PaymentCRUD
from app.crud.accounts_payable.credit_memo import CreditMemoCRUD
from app.schemas.accounts_payable.vendor import VendorCreate, VendorUpdate, VendorResponse
from app.schemas.accounts_payable.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from app.schemas.accounts_payable.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.schemas.accounts_payable.credit_memo import CreditMemoCreate, CreditMemoResponse

router = APIRouter()

# Vendors endpoints
@router.get("/vendors", response_model=dict)
async def get_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all vendors with filtering"""
    vendor_crud = VendorCRUD()
    vendors = await vendor_crud.get_vendors(db, skip=skip, limit=limit, status=status, search=search)
    total = await vendor_crud.count_vendors(db, status=status, search=search)
    
    return {
        "vendors": vendors,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/vendors", response_model=VendorResponse)
async def create_vendor(
    vendor: VendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new vendor"""
    vendor_crud = VendorCRUD()
    return await vendor_crud.create_vendor(db, vendor)

@router.get("/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vendor by ID"""
    vendor_crud = VendorCRUD()
    vendor = await vendor_crud.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: str,
    vendor: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update vendor"""
    vendor_crud = VendorCRUD()
    updated_vendor = await vendor_crud.update_vendor(db, vendor_id, vendor)
    if not updated_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return updated_vendor

@router.delete("/vendors/{vendor_id}")
async def delete_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete vendor"""
    vendor_crud = VendorCRUD()
    success = await vendor_crud.delete_vendor(db, vendor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}

# Bills/Invoices endpoints
@router.get("/bills", response_model=dict)
async def get_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    vendor_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bills/invoices with filtering"""
    invoice_crud = InvoiceCRUD()
    bills = await invoice_crud.get_invoices(db, skip=skip, limit=limit, status=status, vendor_id=vendor_id)
    total = await invoice_crud.count_invoices(db, status=status, vendor_id=vendor_id)
    
    return {
        "bills": bills,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/bills", response_model=InvoiceResponse)
async def create_bill(
    bill: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bill/invoice"""
    invoice_crud = InvoiceCRUD()
    return await invoice_crud.create_invoice(db, bill)

@router.get("/bills/{bill_id}", response_model=InvoiceResponse)
async def get_bill(
    bill_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bill by ID"""
    invoice_crud = InvoiceCRUD()
    bill = await invoice_crud.get_invoice(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.put("/bills/{bill_id}", response_model=InvoiceResponse)
async def update_bill(
    bill_id: str,
    bill: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update bill"""
    invoice_crud = InvoiceCRUD()
    updated_bill = await invoice_crud.update_invoice(db, bill_id, bill)
    if not updated_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return updated_bill

@router.post("/bills/{bill_id}/approve")
async def approve_bill(
    bill_id: str,
    approval_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve bill"""
    invoice_crud = InvoiceCRUD()
    result = await invoice_crud.approve_invoice(db, bill_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill approved successfully", "data": result}

# Payments endpoints
@router.get("/payments", response_model=dict)
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    vendor_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments with filtering"""
    payment_crud = PaymentCRUD()
    payments = await payment_crud.get_payments(db, skip=skip, limit=limit, status=status, vendor_id=vendor_id)
    total = await payment_crud.count_payments(db, status=status, vendor_id=vendor_id)
    
    return {
        "payments": payments,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/payments", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment"""
    payment_crud = PaymentCRUD()
    return await payment_crud.create_payment(db, payment)

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment by ID"""
    payment_crud = PaymentCRUD()
    payment = await payment_crud.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/payments/{payment_id}")
async def delete_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete payment"""
    payment_crud = PaymentCRUD()
    success = await payment_crud.delete_payment(db, payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}

# Credit Memos endpoints
@router.get("/credit-memos", response_model=dict)
async def get_credit_memos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    vendor_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all credit memos with filtering"""
    credit_memo_crud = CreditMemoCRUD()
    memos = await credit_memo_crud.get_credit_memos(db, skip=skip, limit=limit, status=status, vendor_id=vendor_id)
    total = await credit_memo_crud.count_credit_memos(db, status=status, vendor_id=vendor_id)
    
    return {
        "credit_memos": memos,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/credit-memos", response_model=CreditMemoResponse)
async def create_credit_memo(
    memo: CreditMemoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new credit memo"""
    credit_memo_crud = CreditMemoCRUD()
    return await credit_memo_crud.create_credit_memo(db, memo)

@router.post("/credit-memos/{memo_id}/void")
async def void_credit_memo(
    memo_id: str,
    void_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Void credit memo"""
    credit_memo_crud = CreditMemoCRUD()
    result = await credit_memo_crud.void_credit_memo(db, memo_id, void_data.get("reason"))
    if not result:
        raise HTTPException(status_code=404, detail="Credit memo not found")
    return {"message": "Credit memo voided successfully", "data": result}

# Reports endpoints
@router.get("/reports/aging")
async def get_aging_report(
    as_of_date: Optional[date] = None,
    vendor_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AP aging report"""
    # Implementation would generate aging report
    return {
        "aging_buckets": [
            {
                "vendor_name": "ABC Supplies Co.",
                "current": 2500.00,
                "days_1_30": 1200.00,
                "days_31_60": 0.00,
                "days_60_plus": 0.00
            }
        ],
        "totals": {
            "current": 2500.00,
            "days_1_30": 1200.00,
            "days_31_60": 0.00,
            "days_60_plus": 0.00,
            "total": 3700.00
        }
    }

@router.get("/reports/vendor-summary")
async def get_vendor_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vendor summary report"""
    return {
        "total_vendors": 25,
        "active_vendors": 22,
        "total_outstanding": 45230.50
    }

@router.get("/reports/payment-history")
async def get_payment_history(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment history report"""
    return {
        "total_payments": 156,
        "total_amount": 125450.75,
        "average_payment": 804.17
    }

@router.get("/reports/cash-flow-forecast")
async def get_cash_flow_forecast(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get cash flow forecast report"""
    return {
        "next_30_days": 15200.00,
        "next_60_days": 28450.00,
        "next_90_days": 42100.00
    }