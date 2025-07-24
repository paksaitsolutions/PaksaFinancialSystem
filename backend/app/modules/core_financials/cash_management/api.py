

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from datetime import date
from app.core.db.session import get_db
from .services import BankAccountService, TransactionService, ReconciliationService
from . import schemas

router = APIRouter()

def get_bank_account_service(db: Session = Depends(get_db)):
    return BankAccountService(db)

def get_transaction_service(db: Session = Depends(get_db)):
    return TransactionService(db)

def get_reconciliation_service(db: Session = Depends(get_db)):
    return ReconciliationService(db)

# --- Bank Account Endpoints ---

@router.post('/bank-accounts', response_model=schemas.BankAccountResponse, status_code=status.HTTP_201_CREATED)
def create_bank_account(account: schemas.BankAccountCreate, user_id: UUID, service: BankAccountService = Depends(get_bank_account_service)):
    return service.create_bank_account(account, user_id)

@router.get('/bank-accounts', response_model=List[schemas.BankAccountResponse])
def list_bank_accounts(skip: int = 0, limit: int = 100, search: Optional[str] = None, service: BankAccountService = Depends(get_bank_account_service)):
    accounts, _ = service.list_bank_accounts(skip=skip, limit=limit, search=search)
    return accounts

@router.get('/bank-accounts/{account_id}', response_model=schemas.BankAccountResponse)
def get_bank_account(account_id: UUID, service: BankAccountService = Depends(get_bank_account_service)):
    return service.get_bank_account(account_id)

@router.put('/bank-accounts/{account_id}', response_model=schemas.BankAccountResponse)
def update_bank_account(account_id: UUID, account_update: schemas.BankAccountUpdate, user_id: UUID, service: BankAccountService = Depends(get_bank_account_service)):
    return service.update_bank_account(account_id, account_update, user_id)

@router.delete('/bank-accounts/{account_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_bank_account(account_id: UUID, service: BankAccountService = Depends(get_bank_account_service)):
    service.delete_bank_account(account_id)
    return None

# --- Transaction Endpoints ---

@router.post('/transactions', response_model=schemas.BankTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: schemas.BankTransactionCreate, user_id: UUID, service: TransactionService = Depends(get_transaction_service)):
    return service.create_transaction(transaction, user_id)

@router.get('/transactions', response_model=List[schemas.BankTransactionResponse])
def list_transactions(
    account_id: Optional[UUID] = None,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    transaction_type: Optional[schemas.TransactionType] = None,
    status: Optional[schemas.TransactionStatus] = None,
    skip: int = 0,
    limit: int = 100,
    service: TransactionService = Depends(get_transaction_service)
):
    transactions, _ = service.list_transactions(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        status=status,
        skip=skip,
        limit=limit
    )
    return transactions

@router.get('/transactions/{transaction_id}', response_model=schemas.BankTransactionResponse)
def get_transaction(transaction_id: UUID, service: TransactionService = Depends(get_transaction_service)):
    return service.get_transaction(transaction_id)

# --- Reconciliation Endpoints ---

@router.post('/reconciliations', response_model=schemas.BankReconciliationResponse, status_code=status.HTTP_201_CREATED)
def create_reconciliation(reconciliation: schemas.BankReconciliationCreate, user_id: UUID, service: ReconciliationService = Depends(get_reconciliation_service)):
    return service.create_reconciliation(reconciliation, user_id)

@router.get('/reconciliations/{reconciliation_id}', response_model=schemas.BankReconciliationResponse)
def get_reconciliation(reconciliation_id: UUID, service: ReconciliationService = Depends(get_reconciliation_service)):
    return service.get_reconciliation(reconciliation_id)

# Add more endpoints as needed for update/delete/list reconciliations, cash flow, etc.
