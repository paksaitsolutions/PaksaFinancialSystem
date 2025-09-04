"""
Enhanced Financial API with complete CRUD operations and business logic
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.auth_enhanced import get_current_user, require_permission
from app.services.financial_service import FinancialService
from app.models.financial_core import *
from app.schemas.financial_schemas import *

router = APIRouter()

# Chart of Accounts endpoints
@router.get("/accounts", response_model=List[ChartOfAccountsResponse])
async def get_chart_of_accounts(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("read"))
):
    """Get all chart of accounts"""
    accounts = db.query(ChartOfAccounts).filter(ChartOfAccounts.is_active == True).all()
    return accounts

@router.post("/accounts", response_model=ChartOfAccountsResponse)
async def create_account(
    account: ChartOfAccountsCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Create new chart of account"""
    # Check if account code exists
    existing = db.query(ChartOfAccounts).filter(ChartOfAccounts.account_code == account.account_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists")
    
    db_account = ChartOfAccounts(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.put("/accounts/{account_id}", response_model=ChartOfAccountsResponse)
async def update_account(
    account_id: str,
    account: ChartOfAccountsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Update chart of account"""
    db_account = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for field, value in account.dict(exclude_unset=True).items():
        setattr(db_account, field, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account

# Journal Entry endpoints
@router.get("/journal-entries")
async def get_journal_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("read"))
):
    """Get journal entries with pagination and filtering"""
    query = db.query(JournalEntry)
    
    if status:
        query = query.filter(JournalEntry.status == status)
    
    entries = query.offset(skip).limit(limit).all()
    return entries

@router.post("/journal-entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Create new journal entry"""
    financial_service = FinancialService(db)
    
    try:
        journal_entry = financial_service.create_journal_entry(entry, current_user.id)
        return journal_entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/journal-entries/{entry_id}/approve")
async def approve_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("approve"))
):
    """Approve journal entry"""
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    if entry.status != 'draft':
        raise HTTPException(status_code=400, detail="Only draft entries can be approved")
    
    entry.status = 'approved'
    entry.approved_by = current_user.id
    entry.approved_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Journal entry approved successfully"}

@router.post("/journal-entries/{entry_id}/post")
async def post_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("approve"))
):
    """Post journal entry and update account balances"""
    financial_service = FinancialService(db)
    
    try:
        entry = financial_service.post_journal_entry(entry_id, current_user.id)
        return {"message": "Journal entry posted successfully", "entry_id": entry.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Vendor endpoints
@router.get("/vendors", response_model=List[VendorResponse])
async def get_vendors(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("read"))
):
    """Get all vendors"""
    vendors = db.query(Vendor).filter(Vendor.is_active == True).all()
    return vendors

@router.post("/vendors", response_model=VendorResponse)
async def create_vendor(
    vendor: VendorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Create new vendor"""
    # Check if vendor code exists
    existing = db.query(Vendor).filter(Vendor.vendor_code == vendor.vendor_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vendor code already exists")
    
    db_vendor = Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

# Customer endpoints
@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("read"))
):
    """Get all customers"""
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    return customers

@router.post("/customers", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Create new customer"""
    # Check if customer code exists
    existing = db.query(Customer).filter(Customer.customer_code == customer.customer_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer code already exists")
    
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# Bill endpoints
@router.get("/bills", response_model=List[BillResponse])
async def get_bills(
    status: Optional[str] = Query(None),
    vendor_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("read"))
):
    """Get bills with filtering"""
    query = db.query(Bill)
    
    if status:
        query = query.filter(Bill.status == status)
    if vendor_id:
        query = query.filter(Bill.vendor_id == vendor_id)
    
    bills = query.all()
    return bills

@router.post("/bills", response_model=BillResponse)
async def create_bill(
    bill: BillCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Create new bill"""
    # Generate bill number
    bill_number = f"BILL-{datetime.now().strftime('%Y%m%d')}-{db.query(Bill).count() + 1:04d}"
    
    db_bill = Bill(
        bill_number=bill_number,
        **bill.dict()
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

# Invoice endpoints
@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    status: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("read"))
):
    """Get invoices with filtering"""
    query = db.query(Invoice)
    
    if status:
        query = query.filter(Invoice.status == status)
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    invoices = query.all()
    return invoices

@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Create new invoice"""
    # Generate invoice number
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{db.query(Invoice).count() + 1:04d}"
    
    db_invoice = Invoice(
        invoice_number=invoice_number,
        **invoice.dict()
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

# Payment endpoints
@router.post("/vendor-payments", response_model=PaymentResponse)
async def create_vendor_payment(
    payment: VendorPaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Create vendor payment"""
    # Generate payment number
    payment_number = f"VP-{datetime.now().strftime('%Y%m%d')}-{db.query(VendorPayment).count() + 1:04d}"
    
    db_payment = VendorPayment(
        payment_number=payment_number,
        **payment.dict()
    )
    
    # Update bill paid amount if bill_id provided
    if payment.bill_id:
        bill = db.query(Bill).filter(Bill.id == payment.bill_id).first()
        if bill:
            bill.paid_amount += payment.amount
            if bill.paid_amount >= bill.total_amount:
                bill.status = 'paid'
            elif bill.paid_amount > 0:
                bill.status = 'partial'
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.post("/customer-payments", response_model=PaymentResponse)
async def create_customer_payment(
    payment: CustomerPaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("write"))
):
    """Create customer payment"""
    # Generate payment number
    payment_number = f"CP-{datetime.now().strftime('%Y%m%d')}-{db.query(CustomerPayment).count() + 1:04d}"
    
    db_payment = CustomerPayment(
        payment_number=payment_number,
        **payment.dict()
    )
    
    # Update invoice paid amount if invoice_id provided
    if payment.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
        if invoice:
            invoice.paid_amount += payment.amount
            if invoice.paid_amount >= invoice.total_amount:
                invoice.status = 'paid'
            elif invoice.paid_amount > 0:
                invoice.status = 'partial'
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Reports endpoints
@router.get("/reports/trial-balance")
async def get_trial_balance(
    as_of_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("read"))
):
    """Get trial balance report"""
    financial_service = FinancialService(db)
    return financial_service.get_trial_balance(as_of_date)

@router.get("/reports/financial-statements")
async def get_financial_statements(
    period_start: datetime = Query(...),
    period_end: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("read"))
):
    """Get financial statements (Balance Sheet, Income Statement)"""
    financial_service = FinancialService(db)
    return financial_service.generate_financial_statements(period_start, period_end)

@router.post("/period-close")
async def close_period(
    period_end: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("approve"))
):
    """Close accounting period"""
    financial_service = FinancialService(db)
    
    try:
        result = financial_service.process_period_close(period_end, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))