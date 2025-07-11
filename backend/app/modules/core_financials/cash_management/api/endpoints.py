"""
API endpoints for the Cash Management module.
"""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db, get_async_db
from app.core.security import get_current_user
from . import schemas, services
from .exceptions import (
    BankAccountNotFound,
    BankTransactionNotFound,
    ReconciliationNotFound,
    CashManagementError
)

router = APIRouter(prefix="/cash-management", tags=["cash-management"])

def get_bank_account_service(db: Session = Depends(get_db)) -> services.BankAccountService:
    return services.BankAccountService(db)

def get_transaction_service(db: Session = Depends(get_db)) -> services.BankTransactionService:
    return services.BankTransactionService(db)

def get_reconciliation_service(db: Session = Depends(get_db)) -> services.ReconciliationService:
    return services.ReconciliationService(db)

# --- Bank Account Endpoints ---
@router.post("/accounts", response_model=schemas.BankAccountResponse, status_code=status.HTTP_201_CREATED)
def create_bank_account(
    account: schemas.BankAccountCreate,
    service: services.BankAccountService = Depends(get_bank_account_service),
    current_user = Depends(get_current_user)
):
    try:
        return service.create_bank_account(account, current_user.id)
    except CashManagementError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts/{account_id}", response_model=schemas.BankAccountResponse)
def get_bank_account(
    account_id: UUID,
    service: services.BankAccountService = Depends(get_bank_account_service)
):
    try:
        return service.get_bank_account(account_id)
    except BankAccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Transaction Endpoints ---
@router.post("/transactions", response_model=schemas.BankTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: schemas.BankTransactionCreate,
    service: services.BankTransactionService = Depends(get_transaction_service),
    current_user = Depends(get_current_user)
):
    try:
        return service.create_transaction(transaction, current_user.id)
    except CashManagementError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/{transaction_id}", response_model=schemas.BankTransactionResponse)
def get_transaction(
    transaction_id: UUID,
    service: services.BankTransactionService = Depends(get_transaction_service)
):
    try:
        return service.get_transaction(transaction_id)
    except BankTransactionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Reconciliation Endpoints ---
@router.post("/reconciliations", response_model=schemas.BankReconciliationResponse, status_code=status.HTTP_201_CREATED)
def create_reconciliation(
    reconciliation: schemas.BankReconciliationCreate,
    service: services.ReconciliationService = Depends(get_reconciliation_service),
    current_user = Depends(get_current_user)
):
    try:
        return service.create_reconciliation(reconciliation, current_user.id)
    except CashManagementError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reconciliations/{reconciliation_id}", response_model=schemas.BankReconciliationResponse)
def get_reconciliation(
    reconciliation_id: UUID,
    service: services.ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        return service.get_reconciliation(reconciliation_id)
    except ReconciliationNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Bank Account List, Update, Delete ---
@router.get("/accounts", response_model=List[schemas.BankAccountResponse])
def list_bank_accounts(
    skip: int = 0,
    limit: int = 100,
    service: services.BankAccountService = Depends(get_bank_account_service)
):
    return service.list_bank_accounts(skip=skip, limit=limit)

@router.put("/accounts/{account_id}", response_model=schemas.BankAccountResponse)
def update_bank_account(
    account_id: UUID,
    account_update: schemas.BankAccountUpdate,
    service: services.BankAccountService = Depends(get_bank_account_service)
):
    try:
        return service.update_bank_account(account_id, account_update)
    except BankAccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bank_account(
    account_id: UUID,
    service: services.BankAccountService = Depends(get_bank_account_service)
):
    try:
        service.delete_bank_account(account_id)
    except BankAccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Transaction List, Update, Delete ---
@router.get("/transactions", response_model=List[schemas.BankTransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    service: services.BankTransactionService = Depends(get_transaction_service)
):
    return service.list_transactions(skip=skip, limit=limit)

@router.put("/transactions/{transaction_id}", response_model=schemas.BankTransactionResponse)
def update_transaction(
    transaction_id: UUID,
    transaction_update: schemas.BankTransactionUpdate,
    service: services.BankTransactionService = Depends(get_transaction_service)
):
    try:
        return service.update_transaction(transaction_id, transaction_update)
    except BankTransactionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: UUID,
    service: services.BankTransactionService = Depends(get_transaction_service)
):
    try:
        service.delete_transaction(transaction_id)
    except BankTransactionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Reconciliation List, Update, Delete ---
@router.get("/reconciliations", response_model=List[schemas.BankReconciliationResponse])
def list_reconciliations(
    skip: int = 0,
    limit: int = 100,
    service: services.ReconciliationService = Depends(get_reconciliation_service)
):
    return service.list_reconciliations(skip=skip, limit=limit)

@router.put("/reconciliations/{reconciliation_id}", response_model=schemas.BankReconciliationResponse)
def update_reconciliation(
    reconciliation_id: UUID,
    reconciliation_update: schemas.BankReconciliationUpdate,
    service: services.ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        return service.update_reconciliation(reconciliation_id, reconciliation_update)
    except ReconciliationNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/reconciliations/{reconciliation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reconciliation(
    reconciliation_id: UUID,
    service: services.ReconciliationService = Depends(get_reconciliation_service)
):
    try:
        service.delete_reconciliation(reconciliation_id)
    except ReconciliationNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Reporting Endpoints ---
@router.get("/accounts/{account_id}/statement", response_model=schemas.BankAccountStatementResponse)
def get_account_statement(
    account_id: UUID,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: services.BankAccountService = Depends(get_bank_account_service)
):
    """Get a bank account statement for a given period."""
    return service.get_account_statement(account_id, start_date, end_date)

@router.get("/transactions/report", response_model=List[schemas.BankTransactionResponse])
def get_transaction_report(
    account_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: services.BankTransactionService = Depends(get_transaction_service)
):
    """Get a report of transactions filtered by account and date range."""
    return service.get_transaction_report(account_id, start_date, end_date)

@router.get("/reconciliations/report", response_model=List[schemas.BankReconciliationResponse])
def get_reconciliation_report(
    account_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: services.ReconciliationService = Depends(get_reconciliation_service)
):
    """Get a report of reconciliations filtered by account and date range."""
    return service.get_reconciliation_report(account_id, start_date, end_date)

@router.get("/accounts/{account_id}/cashflow", response_model=schemas.CashFlowSummary)
def get_cashflow_summary(
    account_id: UUID,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: services.BankAccountService = Depends(get_bank_account_service)
):
    """Get a cash flow summary for a bank account over a period."""
    return service.get_cashflow_summary(account_id, start_date, end_date)

@router.get("/accounts/{account_id}/reconciliations/summary", response_model=schemas.ReconciliationSummary)
def get_reconciliation_summary(
    account_id: UUID,
    statement_date: Optional[str] = None,
    service: services.ReconciliationService = Depends(get_reconciliation_service)
):
    """Get a summary of reconciliations for a bank account and statement date."""
    return service.get_reconciliation_summary(account_id, statement_date)

# --- Utility & Import Endpoints ---
@router.post("/transactions/import", response_model=List[schemas.BankTransactionResponse])
def import_transactions(
    account_id: UUID,
    transactions: List[dict],
    format: str = "csv",
    options: Optional[dict] = None,
    service: services.BankTransactionService = Depends(get_transaction_service),
    current_user = Depends(get_current_user)
):
    """Import transactions for a bank account from a file or data payload."""
    return service.import_transactions(account_id, transactions, format, options or {}, current_user.id)

@router.get("/accounts/{account_id}/balance", response_model=schemas.BankAccountBalanceResponse)
def get_account_balance(
    account_id: UUID,
    service: services.BankAccountService = Depends(get_bank_account_service)
):
    """Get the current balance for a bank account."""
    return service.get_account_balance(account_id)

# --- Health Check Endpoint ---
@router.get("/health", response_model=dict)
def health_check():
    """Check if the cash management module is healthy."""
    return {"status": "ok"}

@router.get("/forecasting", response_model=schemas.CashForecast)
async def get_cash_forecast(db: AsyncSession = Depends(get_async_db)):
    # Stub: Implement forecasting logic
    return schemas.CashForecast(forecast=[{"date": "2025-07-12", "amount": 12000}])

@router.get("/enhanced-reconciliation", response_model=schemas.EnhancedReconciliationReport)
async def get_enhanced_reconciliation(db: AsyncSession = Depends(get_async_db)):
    # Stub: Implement enhanced reconciliation logic
    return schemas.EnhancedReconciliationReport(details=[{"bank": "Main", "matched": True}])
