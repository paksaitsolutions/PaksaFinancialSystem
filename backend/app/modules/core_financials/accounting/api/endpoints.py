import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import the database session factory using the correct relative path
from ......core.database import get_async_db
from .. import schemas, services
from ..exceptions import AccountingException

# Router for Chart of Accounts
router_accounts = APIRouter()

# Router for Journal Entries
router_journal_entries = APIRouter()

# Dependency for AccountService
def get_account_service(db: AsyncSession = Depends(get_async_db)) -> services.AccountService:
    return services.AccountService(db)

# Dependency for JournalEntryService
def get_journal_entry_service(db: AsyncSession = Depends(get_async_db)) -> services.JournalEntryService:
    return services.JournalEntryService(db)

# --- Chart of Accounts Endpoints ---

@router_accounts.post("/", response_model=schemas.Account, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_in: schemas.AccountCreate,
    service: services.AccountService = Depends(get_account_service),
):
    try:
        return await service.create_account(account_in)
    except AccountingException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router_accounts.get("/", response_model=List[schemas.Account])
async def get_all_accounts(
    service: services.AccountService = Depends(get_account_service),
):
    return await service.get_all_accounts()

@router_accounts.get("/{account_id}", response_model=schemas.Account)
async def get_account(
    account_id: uuid.UUID,
    service: services.AccountService = Depends(get_account_service),
):
    try:
        return await service.get_account_by_id(account_id)
    except AccountingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router_accounts.put("/{account_id}", response_model=schemas.Account)
async def update_account(
    account_id: uuid.UUID,
    account_in: schemas.AccountUpdate,
    service: services.AccountService = Depends(get_account_service),
):
    try:
        return await service.update_account(account_id, account_in)
    except AccountingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router_accounts.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: uuid.UUID,
    service: services.AccountService = Depends(get_account_service),
):
    try:
        await service.delete_account(account_id)
    except AccountingException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Journal Entries Endpoints ---

@router_journal_entries.post("/", response_model=schemas.JournalEntry, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_in: schemas.JournalEntryCreate,
    service: services.JournalEntryService = Depends(get_journal_entry_service),
):
    try:
        return await service.create_journal_entry(entry_in)
    except AccountingException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router_journal_entries.get("/{entry_id}", response_model=schemas.JournalEntry)
async def get_journal_entry(
    entry_id: uuid.UUID,
    service: services.JournalEntryService = Depends(get_journal_entry_service),
):
    try:
        return await service.get_journal_entry_by_id(entry_id)
    except AccountingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router_journal_entries.post("/{entry_id}/post", response_model=schemas.JournalEntry)
async def post_journal_entry(
    entry_id: uuid.UUID,
    service: services.JournalEntryService = Depends(get_journal_entry_service),
):
    """
    Post a journal entry to the general ledger.
    """
    try:
        return await service.post_journal_entry(entry_id)
    except AccountingException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
