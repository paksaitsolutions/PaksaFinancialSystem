"""
API endpoints for the General Ledger (GL) module.
"""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from . import schemas, services
from .exceptions import (
    GLAccountNotFound,
    JournalEntryNotFound,
    GLValidationError
)

router = APIRouter(prefix="/gl", tags=["general-ledger"])

def get_account_service(db: Session = Depends(get_db)) -> services.GLAccountService:
    return services.GLAccountService(db)

def get_journal_entry_service(db: Session = Depends(get_db)) -> services.JournalEntryService:
    return services.JournalEntryService(db)

# --- Chart of Accounts Endpoints ---
@router.post("/accounts", response_model=schemas.GLAccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account: schemas.GLAccountCreate,
    service: services.GLAccountService = Depends(get_account_service),
    current_user = Depends(get_current_user)
):
    try:
        return service.create_account(account, current_user.id)
    except GLValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts/{account_id}", response_model=schemas.GLAccountResponse)
def get_account(
    account_id: UUID,
    service: services.GLAccountService = Depends(get_account_service)
):
    try:
        return service.get_account(account_id)
    except GLAccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/accounts", response_model=List[schemas.GLAccountResponse])
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    service: services.GLAccountService = Depends(get_account_service)
):
    return service.list_accounts(skip=skip, limit=limit)

@router.put("/accounts/{account_id}", response_model=schemas.GLAccountResponse)
def update_account(
    account_id: UUID,
    account_update: schemas.GLAccountUpdate,
    service: services.GLAccountService = Depends(get_account_service)
):
    try:
        return service.update_account(account_id, account_update)
    except GLAccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: UUID,
    service: services.GLAccountService = Depends(get_account_service)
):
    try:
        service.delete_account(account_id)
    except GLAccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Journal Entry Endpoints ---
@router.post("/journal-entries", response_model=schemas.JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    entry: schemas.JournalEntryCreate,
    service: services.JournalEntryService = Depends(get_journal_entry_service),
    current_user = Depends(get_current_user)
):
    try:
        return service.create_journal_entry(entry, current_user.id)
    except GLValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/journal-entries/{entry_id}", response_model=schemas.JournalEntryResponse)
def get_journal_entry(
    entry_id: UUID,
    service: services.JournalEntryService = Depends(get_journal_entry_service)
):
    try:
        return service.get_journal_entry(entry_id)
    except JournalEntryNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/journal-entries", response_model=List[schemas.JournalEntryResponse])
def list_journal_entries(
    skip: int = 0,
    limit: int = 100,
    service: services.JournalEntryService = Depends(get_journal_entry_service)
):
    return service.list_journal_entries(skip=skip, limit=limit)

@router.put("/journal-entries/{entry_id}", response_model=schemas.JournalEntryResponse)
def update_journal_entry(
    entry_id: UUID,
    entry_update: schemas.JournalEntryUpdate,
    service: services.JournalEntryService = Depends(get_journal_entry_service)
):
    try:
        return service.update_journal_entry(entry_id, entry_update)
    except JournalEntryNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/journal-entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(
    entry_id: UUID,
    service: services.JournalEntryService = Depends(get_journal_entry_service)
):
    try:
        service.delete_journal_entry(entry_id)
    except JournalEntryNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Financial Statement Endpoints (Scaffold) ---
@router.get("/statements", response_model=List[schemas.FinancialStatementResponse])
def list_financial_statements(
    period: Optional[str] = None,
    service: services.FinancialStatementService = Depends(services.FinancialStatementService)
):
    return service.list_financial_statements(period=period)

@router.get("/multi-currency-balances", response_model=schemas.MultiCurrencyBalances)
async def get_multi_currency_balances(db: AsyncSession = Depends(get_async_db)):
    # Stub: Implement multi-currency logic
    return schemas.MultiCurrencyBalances(balances={"USD": 10000, "EUR": 8000})

@router.get("/budgeting", response_model=schemas.BudgetReport)
async def get_budget_report(db: AsyncSession = Depends(get_async_db)):
    # Stub: Implement budgeting logic
    return schemas.BudgetReport(budgets=[{"account": "Sales", "budget": 50000, "actual": 48000}])

@router.get("/consolidation", response_model=schemas.ConsolidationReport)
async def get_consolidation_report(db: AsyncSession = Depends(get_async_db)):
    # Stub: Implement consolidation logic
    return schemas.ConsolidationReport(entities=[{"name": "Subsidiary A", "total": 120000}])
