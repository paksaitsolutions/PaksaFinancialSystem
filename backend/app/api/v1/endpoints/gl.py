from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from app.core.database_config import get_db
from app.models.gl_models_updated import GLAccount, JournalEntry, JournalEntryLine, AccountingPeriod
from app.schemas.gl_schemas import (
    GLAccountCreate, GLAccountUpdate, GLAccountInDB,
    JournalEntryCreate, JournalEntryInDB, JournalEntryLineCreate,
    AccountingPeriodCreate, AccountingPeriodInDB
)

router = APIRouter(prefix="/gl", tags=["General Ledger"])

# GL Account Endpoints
@router.post("/accounts/", response_model=GLAccountInDB)
def create_gl_account(account: GLAccountCreate, db: Session = Depends(get_db)):
    """Create a new GL Account"""
    db_account = GLAccount(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/accounts/", response_model=List[GLAccountInDB])
def list_gl_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all GL Accounts"""
    return db.query(GLAccount).offset(skip).limit(limit).all()

@router.get("/accounts/{account_id}", response_model=GLAccountInDB)
def get_gl_account(account_id: int, db: Session = Depends(get_db)):
    """Get a specific GL Account by ID"""
    account = db.query(GLAccount).filter(GLAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="GL Account not found")
    return account

# Journal Entry Endpoints
@router.post("/journal-entries/", response_model=JournalEntryInDB)
def create_journal_entry(entry: JournalEntryCreate, db: Session = Depends(get_db)):
    """Create a new Journal Entry with its lines"""
    # Create the journal entry
    db_entry = JournalEntry(
        entry_number=entry.entry_number,
        entry_date=entry.entry_date,
        reference=entry.reference,
        description=entry.description,
        status='DRAFT'
    )
    db.add(db_entry)
    db.flush()  # Flush to get the entry ID for the lines
    
    # Add journal entry lines
    for line in entry.lines:
        db_line = JournalEntryLine(
            journal_entry_id=db_entry.id,
            account_id=line.account_id,
            line_number=line.line_number,
            debit_amount=line.debit_amount,
            credit_amount=line.credit_amount,
            description=line.description
        )
        db.add(db_line)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/journal-entries/", response_model=List[JournalEntryInDB])
def list_journal_entries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List Journal Entries with optional date filtering"""
    query = db.query(JournalEntry)
    
    if start_date:
        query = query.filter(JournalEntry.entry_date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.entry_date <= end_date)
        
    return query.order_by(JournalEntry.entry_date.desc()).offset(skip).limit(limit).all()

# Accounting Period Endpoints
@router.post("/accounting-periods/", response_model=AccountingPeriodInDB)
def create_accounting_period(period: AccountingPeriodCreate, db: Session = Depends(get_db)):
    """Create a new Accounting Period"""
    db_period = AccountingPeriod(**period.dict())
    db.add(db_period)
    db.commit()
    db.refresh(db_period)
    return db_period

@router.get("/accounting-periods/", response_model=List[AccountingPeriodInDB])
def list_accounting_periods(
    is_closed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List Accounting Periods with optional filtering"""
    query = db.query(AccountingPeriod)
    
    if is_closed is not None:
        query = query.filter(AccountingPeriod.is_closed == is_closed)
        
    return query.order_by(AccountingPeriod.start_date.desc()).offset(skip).limit(limit).all()

# Trial Balance Endpoint
@router.get("/trial-balance/")
def get_trial_balance(as_of_date: date, db: Session = Depends(get_db)):
    """Generate a Trial Balance as of a specific date"""
    # Get all accounts with their balances
    accounts = db.query(GLAccount).filter(GLAccount.is_active == True).all()
    
    trial_balance = []
    
    for account in accounts:
        # Calculate the account balance
        debit_total = db.query(
            func.sum(JournalEntryLine.debit_amount)
        ).join(JournalEntry).filter(
            JournalEntryLine.account_id == account.id,
            JournalEntry.entry_date <= as_of_date,
            JournalEntry.status == 'POSTED'
        ).scalar() or 0
        
        credit_total = db.query(
            func.sum(JournalEntryLine.credit_amount)
        ).join(JournalEntry).filter(
            JournalEntryLine.account_id == account.id,
            JournalEntry.entry_date <= as_of_date,
            JournalEntry.status == 'POSTED'
        ).scalar() or 0
        
        balance = debit_total - credit_total
        
        if balance != 0:  # Only include accounts with non-zero balances
            trial_balance.append({
                'account_code': account.account_code,
                'account_name': account.account_name,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0
            })
    
    return {
        'as_of_date': as_of_date,
        'accounts': trial_balance,
        'total_debits': sum(acct['debit'] for acct in trial_balance),
        'total_credits': sum(acct['credit'] for acct in trial_balance)
    }

# Dashboard Endpoints
@router.get("/dashboard/kpis")
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Get dashboard KPIs for GL module"""
    total_accounts = db.query(GLAccount).filter(GLAccount.is_active == True).count()
    journal_entries = db.query(JournalEntry).count()
    
    # Mock data for demonstration
    return {
        "total_accounts": total_accounts,
        "accounts_change": 5.2,
        "journal_entries": journal_entries,
        "entries_change": 12.4,
        "trial_balance_status": "balanced",
        "trial_balance_difference": 0.00,
        "current_period": "2024-01",
        "period_status": "open",
        "balance_trend": [
            {"period": "2023-09", "assets": 1500000, "liabilities": 800000, "equity": 700000},
            {"period": "2023-10", "assets": 1620000, "liabilities": 850000, "equity": 770000},
            {"period": "2023-11", "assets": 1750000, "liabilities": 900000, "equity": 850000},
            {"period": "2023-12", "assets": 1850000, "liabilities": 950000, "equity": 900000},
            {"period": "2024-01", "assets": 1950000, "liabilities": 1000000, "equity": 950000}
        ],
        "account_distribution": [
            {"type": "Assets", "count": 25},
            {"type": "Liabilities", "count": 15},
            {"type": "Equity", "count": 8},
            {"type": "Revenue", "count": 12},
            {"type": "Expenses", "count": 35}
        ]
    }

@router.get("/journal-entries/recent")
def get_recent_journal_entries(limit: int = 5, db: Session = Depends(get_db)):
    """Get recent journal entries for dashboard"""
    entries = db.query(JournalEntry).order_by(
        JournalEntry.created_at.desc()
    ).limit(limit).all()
    
    return [{
        "id": entry.id,
        "entry_number": entry.entry_number,
        "date": entry.entry_date.isoformat(),
        "description": entry.description,
        "total_amount": 1000.00,  # Would calculate from lines
        "status": entry.status.lower()
    } for entry in entries]
