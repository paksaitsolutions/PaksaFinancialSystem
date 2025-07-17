"""
Cash Management API Endpoints

This module provides API endpoints for managing bank accounts, transactions,
reconciliations, and cash flow forecasting.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

from ...core.database import get_db
from ...core.security import get_current_user
from ...models import User, BankAccount, BankTransaction, BankReconciliation, CashFlowForecast, TransactionMatchingRule
from ...models.enums import BankAccountType, TransactionStatus, CashFlowCategory, ReconciliationStatus, PaymentMethod

router = APIRouter(prefix="/cash-management", tags=["cash-management"])

# Pydantic models for request/response schemas

class BankAccountBase(BaseModel):
    name: str
    account_number: str
    account_type: BankAccountType
    bank_name: str
    bank_code: Optional[str] = None
    branch_name: Optional[str] = None
    iban: Optional[str] = None
    currency_id: UUID
    is_active: bool = True
    include_in_cash_flow: bool = True
    allow_overdraft: bool = False
    overdraft_limit: float = 0.0
    integration_id: Optional[str] = None

class BankAccountCreate(BankAccountBase):
    opening_balance: float = 0.0
    opening_balance_date: date = Field(default_factory=date.today)

class BankAccountUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    include_in_cash_flow: Optional[bool] = None
    allow_overdraft: Optional[bool] = None
    overdraft_limit: Optional[float] = None
    integration_id: Optional[str] = None

class BankAccountResponse(BankAccountBase):
    id: UUID
    current_balance: float
    available_balance: float
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BankTransactionBase(BaseModel):
    transaction_date: date
    value_date: Optional[date] = None
    reference: str
    description: Optional[str] = None
    amount: float
    currency_id: UUID
    exchange_rate: float = 1.0
    category: Optional[CashFlowCategory] = None
    payment_method: Optional[PaymentMethod] = None
    status: TransactionStatus = TransactionStatus.PENDING
    related_document_type: Optional[str] = None
    related_document_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None

class BankTransactionCreate(BankTransactionBase):
    bank_account_id: UUID

class BankTransactionUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[CashFlowCategory] = None
    payment_method: Optional[PaymentMethod] = None
    status: Optional[TransactionStatus] = None
    related_document_type: Optional[str] = None
    related_document_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None

class BankTransactionResponse(BankTransactionBase):
    id: UUID
    bank_account_id: UUID
    is_reconciled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BankReconciliationBase(BaseModel):
    statement_date: date
    statement_balance: float
    ending_balance: float
    status: ReconciliationStatus = ReconciliationStatus.IN_PROGRESS
    bank_account_id: UUID

class BankReconciliationCreate(BankReconciliationBase):
    transaction_ids: List[UUID] = []

class BankReconciliationUpdate(BaseModel):
    status: Optional[ReconciliationStatus] = None
    ending_balance: Optional[float] = None

class BankReconciliationResponse(BankReconciliationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    transactions: List[BankTransactionResponse] = []

    class Config:
        orm_mode = True

class CashFlowForecastBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    currency_id: UUID
    include_unpaid_invoices: bool = True
    include_unpaid_bills: bool = True
    include_recurring_transactions: bool = True

class CashFlowForecastCreate(CashFlowForecastBase):
    pass

class CashFlowForecastUpdate(BaseModel):
    name: Optional[str] = None
    include_unpaid_invoices: Optional[bool] = None
    include_unpaid_bills: Optional[bool] = None
    include_recurring_transactions: Optional[bool] = None

class CashFlowForecastResponse(CashFlowForecastBase):
    id: UUID
    forecast_data: Optional[Dict[str, Any]] = None
    last_calculated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Bank Account Endpoints

@router.post("/bank-accounts/", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_account(
    account: BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bank account."""
    db_account = BankAccount(**account.dict(exclude={"opening_balance", "opening_balance_date"}))
    db_account.created_by_id = current_user.id
    
    # Set initial balance if provided
    if account.opening_balance != 0:
        db_account.current_balance = account.opening_balance
        db_account.available_balance = account.opening_balance
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    # TODO: Create opening balance transaction if needed
    
    return db_account

@router.get("/bank-accounts/", response_model=List[BankAccountResponse])
async def list_bank_accounts(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    currency_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all bank accounts with optional filtering."""
    query = db.query(BankAccount)
    
    if is_active is not None:
        query = query.filter(BankAccount.is_active == is_active)
    
    if currency_id is not None:
        query = query.filter(BankAccount.currency_id == currency_id)
    
    return query.offset(skip).limit(limit).all()

@router.get("/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific bank account by ID."""
    account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    return account

@router.put("/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def update_bank_account(
    account_id: UUID,
    account_update: BankAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a bank account."""
    db_account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    update_data = account_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_account, field, value)
    
    db_account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_account)
    
    return db_account

@router.delete("/bank-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bank_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a bank account."""
    db_account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    # Prevent deletion of accounts with transactions
    transaction_count = db.query(BankTransaction).filter(BankTransaction.bank_account_id == account_id).count()
    if transaction_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete account with existing transactions"
        )
    
    db.delete(db_account)
    db.commit()
    return None

# Bank Transaction Endpoints

@router.post("/transactions/", response_model=BankTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: BankTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bank transaction."""
    # Verify bank account exists
    account = db.query(BankAccount).filter(BankAccount.id == transaction.bank_account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    # Create transaction
    db_transaction = BankTransaction(**transaction.dict())
    db_transaction.created_by_id = current_user.id
    
    # Update account balance if transaction is posted
    if db_transaction.status == TransactionStatus.POSTED:
        account.update_balance(
            Decimal(str(db_transaction.amount)),
            is_credit=db_transaction.amount > 0
        )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/transactions/", response_model=List[BankTransactionResponse])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    bank_account_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[TransactionStatus] = None,
    category: Optional[CashFlowCategory] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List bank transactions with filtering options."""
    query = db.query(BankTransaction)
    
    if bank_account_id is not None:
        query = query.filter(BankTransaction.bank_account_id == bank_account_id)
    
    if start_date is not None:
        query = query.filter(BankTransaction.transaction_date >= start_date)
    
    if end_date is not None:
        query = query.filter(BankTransaction.transaction_date <= end_date)
    
    if status is not None:
        query = query.filter(BankTransaction.status == status)
    
    if category is not None:
        query = query.filter(BankTransaction.category == category)
    
    return query.order_by(BankTransaction.transaction_date.desc()).offset(skip).limit(limit).all()

# Bank Reconciliation Endpoints

@router.post("/reconciliations/", response_model=BankReconciliationResponse, status_code=status.HTTP_201_CREATED)
async def create_reconciliation(
    reconciliation: BankReconciliationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bank reconciliation."""
    # Verify bank account exists
    account = db.query(BankAccount).filter(BankAccount.id == reconciliation.bank_account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    # Create reconciliation
    db_reconciliation = BankReconciliation(**reconciliation.dict(exclude={"transaction_ids"}))
    db_reconciliation.created_by_id = current_user.id
    
    # Add transactions to reconciliation
    if reconciliation.transaction_ids:
        transactions = db.query(BankTransaction).filter(
            BankTransaction.id.in_(reconciliation.transaction_ids)
        ).all()
        
        # Verify all transactions belong to the same account
        for txn in transactions:
            if txn.bank_account_id != reconciliation.bank_account_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Transaction {txn.id} does not belong to the specified bank account"
                )
            
            txn.reconciliation_id = db_reconciliation.id
            txn.is_reconciled = True
    
    db.add(db_reconciliation)
    db.commit()
    db.refresh(db_reconciliation)
    
    return db_reconciliation

# Cash Flow Forecast Endpoints

@router.post("/forecasts/", response_model=CashFlowForecastResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast(
    forecast: CashFlowForecastCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new cash flow forecast."""
    db_forecast = CashFlowForecast(**forecast.dict())
    db_forecast.created_by_id = current_user.id
    
    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)
    
    return db_forecast

@router.post("/forecasts/{forecast_id}/generate", response_model=CashFlowForecastResponse)
async def generate_forecast(
    forecast_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate or update a cash flow forecast."""
    db_forecast = db.query(CashFlowForecast).filter(CashFlowForecast.id == forecast_id).first()
    if not db_forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    
    # Generate forecast data
    forecast_data = db_forecast.generate_forecast(db)
    
    db_forecast.forecast_data = forecast_data
    db_forecast.last_calculated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_forecast)
    
    return db_forecast
