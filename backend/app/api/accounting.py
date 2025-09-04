# -*- coding: utf-8 -*-
"""
Comprehensive Accounting API
---------------------------
Complete API endpoints for GL, AP, AR, Budget, Tax
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.accounting import *
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter()

# Pydantic schemas
class ChartOfAccountsCreate(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    parent_id: Optional[int] = None

class ChartOfAccountsResponse(BaseModel):
    id: int
    account_code: str
    account_name: str
    account_type: str
    balance: float
    is_active: bool
    
    class Config:
        from_attributes = True

class JournalEntryLineCreate(BaseModel):
    account_id: int
    description: str
    debit_amount: Decimal = 0
    credit_amount: Decimal = 0

class JournalEntryCreate(BaseModel):
    entry_date: date
    description: str
    reference: Optional[str] = None
    lines: List[JournalEntryLineCreate]

class VendorCreate(BaseModel):
    vendor_code: str
    vendor_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(BaseModel):
    customer_code: str
    customer_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Decimal = 0

class BillCreate(BaseModel):
    vendor_id: int
    bill_date: date
    due_date: date
    total_amount: Decimal

class InvoiceCreate(BaseModel):
    customer_id: int
    invoice_date: date
    due_date: date
    total_amount: Decimal

class PaymentCreate(BaseModel):
    payment_date: date
    amount: Decimal
    payment_method: str
    reference: Optional[str] = None
    bill_id: Optional[int] = None
    invoice_id: Optional[int] = None

# Chart of Accounts endpoints
@router.get("/accounts", response_model=List[ChartOfAccountsResponse])
def get_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    accounts = db.query(ChartOfAccounts).filter(ChartOfAccounts.is_active == True).offset(skip).limit(limit).all()
    return accounts

@router.post("/accounts", response_model=ChartOfAccountsResponse)
def create_account(
    account: ChartOfAccountsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_account = ChartOfAccounts(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

# Journal Entry endpoints
@router.post("/journal-entries")
def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate entry number
    entry_count = db.query(JournalEntry).count()
    entry_number = f"JE-{entry_count + 1:06d}"
    
    # Calculate totals
    total_debit = sum(line.debit_amount for line in entry.lines)
    total_credit = sum(line.credit_amount for line in entry.lines)
    
    if total_debit != total_credit:
        raise HTTPException(status_code=400, detail="Debits must equal credits")
    
    # Create journal entry
    db_entry = JournalEntry(
        entry_number=entry_number,
        entry_date=entry.entry_date,
        description=entry.description,
        reference=entry.reference,
        total_debit=total_debit,
        total_credit=total_credit,
        created_by=current_user.id
    )
    db.add(db_entry)
    db.flush()
    
    # Create lines
    for line in entry.lines:
        db_line = JournalEntryLine(
            journal_entry_id=db_entry.id,
            account_id=line.account_id,
            description=line.description,
            debit_amount=line.debit_amount,
            credit_amount=line.credit_amount
        )
        db.add(db_line)
        
        # Update account balance
        account = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == line.account_id).first()
        if account:
            if account.account_type in ['ASSET', 'EXPENSE']:
                account.balance += line.debit_amount - line.credit_amount
            else:
                account.balance += line.credit_amount - line.debit_amount
    
    db.commit()
    return {"id": db_entry.id, "entry_number": entry_number, "status": "created"}

# Vendor endpoints
@router.get("/vendors")
def get_vendors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vendors = db.query(Vendor).filter(Vendor.is_active == True).offset(skip).limit(limit).all()
    return vendors

@router.post("/vendors")
def create_vendor(
    vendor: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_vendor = Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

# Customer endpoints
@router.get("/customers")
def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customers = db.query(Customer).filter(Customer.is_active == True).offset(skip).limit(limit).all()
    return customers

@router.post("/customers")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# Bill endpoints
@router.get("/bills")
def get_bills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bills = db.query(Bill).offset(skip).limit(limit).all()
    return bills

@router.post("/bills")
def create_bill(
    bill: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate bill number
    bill_count = db.query(Bill).count()
    bill_number = f"BILL-{bill_count + 1:06d}"
    
    db_bill = Bill(
        bill_number=bill_number,
        **bill.dict()
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

# Invoice endpoints
@router.get("/invoices")
def get_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return invoices

@router.post("/invoices")
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate invoice number
    invoice_count = db.query(Invoice).count()
    invoice_number = f"INV-{invoice_count + 1:06d}"
    
    db_invoice = Invoice(
        invoice_number=invoice_number,
        **invoice.dict()
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

# Payment endpoints
@router.post("/payments")
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate payment number
    payment_count = db.query(Payment).count()
    payment_number = f"PAY-{payment_count + 1:06d}"
    
    db_payment = Payment(
        payment_number=payment_number,
        **payment.dict()
    )
    db.add(db_payment)
    
    # Update bill or invoice
    if payment.bill_id:
        bill = db.query(Bill).filter(Bill.id == payment.bill_id).first()
        if bill:
            bill.paid_amount += payment.amount
            if bill.paid_amount >= bill.total_amount:
                bill.status = 'PAID'
    
    if payment.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
        if invoice:
            invoice.paid_amount += payment.amount
            if invoice.paid_amount >= invoice.total_amount:
                invoice.status = 'PAID'
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Trial Balance
@router.get("/trial-balance")
def get_trial_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    accounts = db.query(ChartOfAccounts).filter(ChartOfAccounts.is_active == True).all()
    
    trial_balance = []
    total_debit = 0
    total_credit = 0
    
    for account in accounts:
        balance = float(account.balance)
        debit_amount = balance if balance > 0 else 0
        credit_amount = abs(balance) if balance < 0 else 0
        
        trial_balance.append({
            "account_code": account.account_code,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "debit_amount": debit_amount,
            "credit_amount": credit_amount,
            "balance": balance
        })
        
        total_debit += debit_amount
        total_credit += credit_amount
    
    return {
        "entries": trial_balance,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "is_balanced": abs(total_debit - total_credit) < 0.01
    }