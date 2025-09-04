"""
Financial Core API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_enhanced import get_current_user
from app.services.financial_core import *
from app.schemas.financial_schemas import *
from typing import List
from datetime import date
from decimal import Decimal

router = APIRouter(prefix="/api/financial", tags=["Financial Core"])

# Double-Entry Accounting Endpoints
@router.post("/journal-entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a balanced journal entry"""
    try:
        entry = DoubleEntryService.create_journal_entry(
            db, entry_data.dict(), current_user.id
        )
        return entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/journal-entries/{entry_id}/approve")
async def approve_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve journal entry"""
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    if entry.status != 'pending':
        raise HTTPException(status_code=400, detail="Entry must be pending to approve")
    
    entry.status = 'approved'
    entry.approved_by = current_user.id
    entry.approved_at = datetime.now()
    db.commit()
    
    return {"message": "Journal entry approved", "entry_id": entry_id}

@router.post("/journal-entries/{entry_id}/post")
async def post_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Post journal entry and update account balances"""
    try:
        entry = DoubleEntryService.post_journal_entry(db, entry_id, current_user.id)
        return {"message": "Journal entry posted", "entry_id": entry_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/journal-entries/validate")
async def validate_journal_entry(lines: List[dict]):
    """Validate if journal entry lines are balanced"""
    is_balanced = DoubleEntryService.validate_journal_entry(lines)
    return {"is_balanced": is_balanced}

# Period Closing Endpoints
@router.post("/period-closing")
async def close_accounting_period(
    period_end: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Close accounting period"""
    try:
        result = PeriodClosingService.close_period(db, period_end, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/period-closing/status")
async def get_period_status(
    period_end: date,
    db: Session = Depends(get_db)
):
    """Check if period can be closed"""
    unposted = db.query(JournalEntry).filter(
        and_(
            JournalEntry.entry_date <= period_end,
            JournalEntry.status != 'posted'
        )
    ).count()
    
    return {
        "can_close": unposted == 0,
        "unposted_entries": unposted,
        "period_end": period_end
    }

# Multi-Currency Endpoints
@router.get("/currency/exchange-rate")
async def get_exchange_rate(
    from_currency: str,
    to_currency: str,
    rate_date: date = None
):
    """Get exchange rate between currencies"""
    rate = MultiCurrencyService.get_exchange_rate(from_currency, to_currency, rate_date)
    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "rate": rate,
        "rate_date": rate_date or date.today()
    }

@router.post("/currency/convert")
async def convert_currency(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    rate_date: date = None
):
    """Convert amount between currencies"""
    converted = MultiCurrencyService.convert_amount(amount, from_currency, to_currency, rate_date)
    rate = MultiCurrencyService.get_exchange_rate(from_currency, to_currency, rate_date)
    
    return {
        "original_amount": amount,
        "from_currency": from_currency,
        "converted_amount": converted,
        "to_currency": to_currency,
        "exchange_rate": rate,
        "rate_date": rate_date or date.today()
    }

@router.post("/currency/journal-entry", response_model=JournalEntryResponse)
async def create_currency_conversion_entry(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create journal entry for currency conversion"""
    try:
        entry = MultiCurrencyService.create_currency_journal_entry(
            db, amount, from_currency, to_currency, current_user.id
        )
        return entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Tax Calculation Endpoints
@router.post("/tax/calculate")
async def calculate_tax(
    amount: Decimal,
    tax_rate: Decimal,
    tax_type: str = "sales"
):
    """Calculate tax on amount"""
    calculation = TaxCalculationService.calculate_sales_tax(amount, tax_rate, tax_type)
    return calculation

@router.post("/tax/journal-entry", response_model=JournalEntryResponse)
async def create_tax_journal_entry(
    invoice_id: str,
    amount: Decimal,
    tax_rate: Decimal,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create journal entry for tax"""
    try:
        tax_calculation = TaxCalculationService.calculate_sales_tax(amount, tax_rate)
        entry = TaxCalculationService.create_tax_journal_entry(
            db, invoice_id, tax_calculation, current_user.id
        )
        return entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Bank Reconciliation Endpoints
@router.post("/bank-reconciliation")
async def reconcile_bank_statement(
    bank_account_id: str,
    statement_data: List[dict],
    statement_date: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reconcile bank statement with book records"""
    try:
        result = BankReconciliationService.reconcile_bank_statement(
            db, bank_account_id, statement_data, statement_date, current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bank-reconciliation/adjustments")
async def create_reconciliation_adjustments(
    reconciliation_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create journal entries for reconciliation adjustments"""
    try:
        adjustments = BankReconciliationService.create_reconciliation_adjustments(
            db, reconciliation_data, current_user.id
        )
        return {"adjustment_entries": adjustments}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Account Balance Endpoints
@router.get("/accounts/{account_id}/balance")
async def get_account_balance(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Get current account balance"""
    account = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {
        "account_id": account_id,
        "account_code": account.account_code,
        "account_name": account.account_name,
        "current_balance": account.current_balance,
        "normal_balance": account.normal_balance
    }

@router.get("/trial-balance")
async def get_trial_balance(
    as_of_date: date = None,
    db: Session = Depends(get_db)
):
    """Get trial balance report"""
    if not as_of_date:
        as_of_date = date.today()
    
    accounts = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.is_active == True
    ).order_by(ChartOfAccounts.account_code).all()
    
    trial_balance = []
    total_debits = Decimal('0')
    total_credits = Decimal('0')
    
    for account in accounts:
        if account.current_balance != 0:
            if account.normal_balance == 'Debit':
                debit_balance = account.current_balance if account.current_balance > 0 else Decimal('0')
                credit_balance = -account.current_balance if account.current_balance < 0 else Decimal('0')
            else:
                credit_balance = account.current_balance if account.current_balance > 0 else Decimal('0')
                debit_balance = -account.current_balance if account.current_balance < 0 else Decimal('0')
            
            trial_balance.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "debit_balance": debit_balance,
                "credit_balance": credit_balance
            })
            
            total_debits += debit_balance
            total_credits += credit_balance
    
    return {
        "as_of_date": as_of_date,
        "accounts": trial_balance,
        "total_debits": total_debits,
        "total_credits": total_credits,
        "is_balanced": abs(total_debits - total_credits) <= Decimal('0.01')
    }