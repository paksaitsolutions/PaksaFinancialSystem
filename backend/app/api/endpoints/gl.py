"""
General Ledger API endpoints.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.services.gl import account_service, journal_service

router = APIRouter()

# Helper functions
def get_account_service(db: Session = Depends(get_db)) -> account_service.AccountService:
    """Get an instance of the account service."""
    return account_service.AccountService(db)

def get_journal_service(db: Session = Depends(get_db)) -> journal_service.JournalEntryService:
    """Get an instance of the journal entry service."""
    return journal_service.JournalEntryService(db)

# Account endpoints
@router.post(
    "/accounts/", 
    response_model=schemas.AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Create a new account in the chart of accounts.",
    response_description="The created account",
    tags=["Chart of Accounts"]
)
async def create_account(
    account_in: schemas.AccountCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new account in the chart of accounts.
    """
    service = get_account_service(db)
    try:
        return service.create_account(account_in, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/accounts/{account_id}",
    response_model=schemas.AccountResponse,
    summary="Get account by ID",
    description="Get detailed information about a specific account.",
    response_description="The requested account",
    tags=["Chart of Accounts"]
)
async def get_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed information about a specific account.
    """
    service = get_account_service(db)
    try:
        account = service.get(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        return account
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/accounts/{account_id}",
    response_model=schemas.AccountResponse,
    summary="Update an account",
    description="Update an existing account in the chart of accounts.",
    response_description="The updated account",
    tags=["Chart of Accounts"]
)
async def update_account(
    account_id: UUID,
    account_in: schemas.AccountUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an existing account in the chart of accounts.
    """
    service = get_account_service(db)
    try:
        account = service.update(account_id, account_in, current_user.id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        return account
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/accounts/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an account",
    description="Delete an account from the chart of accounts.",
    tags=["Chart of Accounts"]
)
async def delete_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an account from the chart of accounts.
    """
    service = get_account_service(db)
    try:
        success = service.delete(account_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or could not be deleted"
            )
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/accounts/",
    response_model=schemas.PaginatedResponse[schemas.AccountResponse],
    summary="List accounts",
    description="List all accounts with optional filtering and pagination.",
    response_description="Paginated list of accounts",
    tags=["Chart of Accounts"]
)
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    query: Optional[str] = None,
    account_type: Optional[schemas.AccountType] = None,
    status: Optional[schemas.AccountStatus] = None,
    company_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all accounts with optional filtering and pagination.
    """
    service = get_account_service(db)
    try:
        filter_params = {
            "skip": skip,
            "limit": limit,
            "query": query,
            "account_type": account_type,
            "status": status,
            "company_id": company_id
        }
        accounts = service.list(filter_params)
        return accounts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/accounts/tree",
    response_model=List[schemas.AccountTreeResponse],
    summary="Get account hierarchy",
    description="Get the complete account hierarchy as a tree structure.",
    response_description="List of root accounts with nested children",
    tags=["Chart of Accounts"]
)
async def get_account_tree(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the complete account hierarchy as a tree structure.
    """
    service = get_account_service(db)
    try:
        return service.get_account_tree(company_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/accounts/{account_id}/balance",
    response_model=schemas.AccountBalanceResponse,
    summary="Get account balance",
    description="Get the current balance of an account.",
    response_description="Account balance information",
    tags=["Chart of Accounts"]
)
async def get_account_balance(
    account_id: UUID,
    as_of_date: Optional[date] = None,
    include_children: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the current balance of an account.
    """
    service = get_account_service(db)
    try:
        return service.get_account_balance(account_id, as_of_date, include_children)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Journal Entry endpoints
@router.post(
    "/journal-entries/",
    response_model=schemas.JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a journal entry",
    description="Create a new journal entry with line items.",
    response_description="The created journal entry",
    tags=["Journal Entries"]
)
async def create_journal_entry(
    entry_in: schemas.JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new journal entry with line items.
    """
    service = get_journal_service(db)
    try:
        return service.create_entry(entry_in, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/journal-entries/{entry_id}",
    response_model=schemas.JournalEntryResponse,
    summary="Get journal entry by ID",
    description="Get detailed information about a specific journal entry.",
    response_description="The requested journal entry",
    tags=["Journal Entries"]
)
async def get_journal_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed information about a specific journal entry.
    """
    service = get_journal_service(db)
    try:
        entry = service.get_entry(entry_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        return entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/journal-entries/{entry_id}",
    response_model=schemas.JournalEntryResponse,
    summary="Update a journal entry",
    description="Update an existing journal entry.",
    response_description="The updated journal entry",
    tags=["Journal Entries"]
)
async def update_journal_entry(
    entry_id: UUID,
    entry_in: schemas.JournalEntryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an existing journal entry.
    """
    service = get_journal_service(db)
    try:
        entry = service.update_entry(entry_id, entry_in, current_user.id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        return entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/journal-entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a journal entry",
    description="Delete a journal entry.",
    tags=["Journal Entries"]
)
async def delete_journal_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a journal entry.
    """
    service = get_journal_service(db)
    try:
        success = service.delete_entry(entry_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found or could not be deleted"
            )
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/journal-entries/",
    response_model=schemas.PaginatedResponse[schemas.JournalEntryResponse],
    summary="List journal entries",
    description="List all journal entries with optional filtering and pagination.",
    response_description="Paginated list of journal entries",
    tags=["Journal Entries"]
)
async def list_journal_entries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[schemas.JournalEntryStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    company_id: Optional[UUID] = None,
    account_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all journal entries with optional filtering and pagination.
    """
    service = get_journal_service(db)
    try:
        filter_params = {
            "skip": skip,
            "limit": limit,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "company_id": company_id,
            "account_id": account_id
        }
        entries = service.list_entries(filter_params)
        return entries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/journal-entries/{entry_id}/post",
    response_model=schemas.JournalEntryResponse,
    summary="Post a journal entry",
    description="Post a draft journal entry to update account balances.",
    response_description="The posted journal entry",
    tags=["Journal Entries"]
)
async def post_journal_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Post a draft journal entry to update account balances.
    """
    service = get_journal_service(db)
    try:
        entry = service.post_entry(entry_id, current_user.id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        return entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/journal-entries/{entry_id}/reverse",
    response_model=schemas.JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reverse a journal entry",
    description="Create a reversing journal entry for an existing posted entry.",
    response_description="The created reversing journal entry",
    tags=["Journal Entries"]
)
async def reverse_journal_entry(
    entry_id: UUID,
    reversal_date: date = date.today(),
    reversal_reference: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a reversing journal entry for an existing posted entry.
    """
    service = get_journal_service(db)
    try:
        return service.reverse_entry(
            entry_id=entry_id,
            reversal_date=reversal_date,
            reversal_reference=reversal_reference,
            created_by=current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Trial Balance endpoints
@router.get(
    "/trial-balance/",
    response_model=List[schemas.TrialBalanceAccountResponse],
    summary="Generate a trial balance",
    description="Generate a trial balance for a specific date range.",
    response_description="List of accounts with their balances",
    tags=["Financial Reports"]
)
async def generate_trial_balance(
    company_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a trial balance for a specific date range.
    """
    service = get_journal_service(db)
    try:
        return service.generate_trial_balance(company_id, start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Financial Statement endpoints
@router.get(
    "/financial-statements/balance-sheet",
    response_model=schemas.FinancialStatementResponse,
    summary="Generate a balance sheet",
    description="Generate a balance sheet for a specific date.",
    response_description="The generated balance sheet",
    tags=["Financial Reports"]
)
async def generate_balance_sheet(
    company_id: UUID,
    as_of_date: date = date.today(),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a balance sheet for a specific date.
    """
    service = get_journal_service(db)
    try:
        return service.generate_balance_sheet(company_id, as_of_date, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/financial-statements/income-statement",
    response_model=schemas.FinancialStatementResponse,
    summary="Generate an income statement",
    description="Generate an income statement for a date range.",
    response_description="The generated income statement",
    tags=["Financial Reports"]
)
async def generate_income_statement(
    company_id: UUID,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate an income statement for a date range.
    """
    service = get_journal_service(db)
    try:
        return service.generate_income_statement(company_id, start_date, end_date, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/financial-statements/cash-flow",
    response_model=schemas.FinancialStatementResponse,
    summary="Generate a cash flow statement",
    description="Generate a cash flow statement for a date range.",
    response_description="The generated cash flow statement",
    tags=["Financial Reports"]
)
async def generate_cash_flow_statement(
    company_id: UUID,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a cash flow statement for a date range.
    """
    service = get_journal_service(db)
    try:
        return service.generate_cash_flow_statement(company_id, start_date, end_date, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
