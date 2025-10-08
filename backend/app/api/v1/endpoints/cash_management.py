from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.cash_management import BankAccount, BankTransaction, TransactionType, TransactionStatus
from app.schemas.cash_management import (
    BankAccountCreate, BankAccountResponse, BankAccountUpdate,
    TransactionCreate, TransactionResponse, CashFlowSummary
)

router = APIRouter()

@router.get("/accounts", response_model=List[BankAccountResponse])
def get_bank_accounts(db: Session = Depends(get_db)):
    accounts = db.query(BankAccount).filter(BankAccount.is_active == True).all()
    return accounts

@router.post("/accounts", response_model=BankAccountResponse)
def create_bank_account(account: BankAccountCreate, db: Session = Depends(get_db)):
    db_account = BankAccount(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.put("/accounts/{account_id}", response_model=BankAccountResponse)
def update_bank_account(account_id: str, account: BankAccountUpdate, db: Session = Depends(get_db)):
    db_account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for field, value in account.dict(exclude_unset=True).items():
        setattr(db_account, field, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    account_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(BankTransaction)
    if account_id:
        query = query.filter(BankTransaction.account_id == account_id)
    
    transactions = query.order_by(desc(BankTransaction.transaction_date)).limit(limit).all()
    return transactions

@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    # Verify account exists
    account = db.query(BankAccount).filter(BankAccount.id == transaction.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db_transaction = BankTransaction(**transaction.dict())
    db.add(db_transaction)
    
    # Update account balance
    if transaction.transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER_IN]:
        account.current_balance += transaction.amount
        account.available_balance += transaction.amount
    else:
        account.current_balance -= transaction.amount
        account.available_balance -= transaction.amount
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/dashboard", response_model=CashFlowSummary)
def get_cash_dashboard(db: Session = Depends(get_db)):
    # Get total cash balance
    total_balance = db.query(func.sum(BankAccount.current_balance)).scalar() or 0
    
    # Get account count
    account_count = db.query(BankAccount).filter(BankAccount.is_active == True).count()
    
    # Get recent transactions count
    recent_transactions = db.query(BankTransaction).count()
    
    # Get pending transactions
    pending_count = db.query(BankTransaction).filter(
        BankTransaction.status == TransactionStatus.PENDING
    ).count()
    
    return {
        "total_balance": float(total_balance),
        "account_count": account_count,
        "recent_transactions": recent_transactions,
        "pending_transactions": pending_count
    }