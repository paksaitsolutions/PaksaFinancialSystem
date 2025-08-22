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
<<<<<<< HEAD
from app.db.session import get_db
=======
from app.core.db.session import get_db
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
from app.services.gl import account_service, journal_service, period_service, financial_statement_service

router = APIRouter()

# Helper functions
def get_account_service(db: Session = Depends(get_db)) -> account_service.AccountService:
    """Get an instance of the account service."""
    return account_service.AccountService(db)

def get_journal_service(db: Session = Depends(get_db)) -> journal_service.JournalEntryService:
    """Get an instance of the journal entry service."""
    return journal_service.JournalEntryService(db)


def get_period_service(db: Session = Depends(get_db)) -> period_service.PeriodService:
    """Get an instance of the period service."""
    return period_service.PeriodService(db)


def get_financial_statement_service(db: Session = Depends(get_db)) -> financial_statement_service.FinancialStatementService:
    """Get an instance of the financial statement service."""
    return financial_statement_service.FinancialStatementService(db)

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

# Accounting Period endpoints
@router.post(
    "/accounting-periods/",
    response_model=schemas.AccountingPeriodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new accounting period",
    description="Create a new accounting period with the specified date range.",
    response_description="The created accounting period",
    tags=["Accounting Periods"]
)
async def create_accounting_period(
    period_in: schemas.AccountingPeriodCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new accounting period.
    """
    service = get_period_service(db)
    try:
        return service.create_period(period_in, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/accounting-periods/{period_id}",
    response_model=schemas.AccountingPeriodResponse,
    summary="Get accounting period by ID",
    description="Get detailed information about a specific accounting period.",
    response_description="The requested accounting period",
    tags=["Accounting Periods"]
)
async def get_accounting_period(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed information about a specific accounting period.
    """
    service = get_period_service(db)
    period = service.get(period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accounting period not found"
        )
    return period


@router.post(
    "/accounting-periods/{period_id}/close",
    response_model=schemas.AccountingPeriodResponse,
    summary="Close an accounting period",
    description="Close an accounting period and generate a trial balance.",
    response_description="The closed accounting period",
    tags=["Accounting Periods"]
)
async def close_accounting_period(
    period_id: UUID,
    force: bool = Query(False, description="Force close even with unposted entries"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Close an accounting period.
    """
    service = get_period_service(db)
    try:
        return service.close_period(period_id, current_user.id, force=force)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/accounting-periods/{period_id}/reopen",
    response_model=schemas.AccountingPeriodResponse,
    summary="Reopen a closed accounting period",
    description="Reopen a closed accounting period.",
    response_description="The reopened accounting period",
    tags=["Accounting Periods"]
)
async def reopen_accounting_period(
    period_id: UUID,
    force: bool = Query(False, description="Force reopen even with subsequent closed periods"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Reopen a closed accounting period.
    """
    service = get_period_service(db)
    try:
        return service.reopen_period(period_id, current_user.id, force=force)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/accounting-periods/company/{company_id}",
    response_model=List[schemas.AccountingPeriodResponse],
    summary="List accounting periods for a company",
    description="List all accounting periods for a specific company with optional filtering.",
    response_description="List of accounting periods",
    tags=["Accounting Periods"]
)
async def list_accounting_periods(
    company_id: UUID,
    is_closed: Optional[bool] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List accounting periods for a company with optional filtering.
    """
    service = get_period_service(db)
    query = db.query(AccountingPeriod).filter(
        AccountingPeriod.company_id == company_id
    )
    
    if is_closed is not None:
        query = query.filter(AccountingPeriod.is_closed == is_closed)
    
    if start_date:
        query = query.filter(AccountingPeriod.start_date >= start_date)
    
    if end_date:
        query = query.filter(AccountingPeriod.end_date <= end_date)
    
    periods = query.order_by(AccountingPeriod.start_date.desc())\
                  .offset(skip).limit(limit).all()
    
    return periods


@router.get(
    "/accounting-periods/company/{company_id}/by-date/{target_date}",
    response_model=schemas.AccountingPeriodResponse,
    summary="Get accounting period by date",
    description="Get the accounting period for a specific date.",
    response_description="The accounting period for the specified date",
    tags=["Accounting Periods"]
)
async def get_accounting_period_by_date(
    company_id: UUID,
    target_date: date = Query(..., description="Date to find the period for"),
    create_if_missing: bool = Query(False, description="Create a new period if none exists"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the accounting period for a specific date.
    """
    service = get_period_service(db)
    try:
        period = service.get_period_by_date(
            company_id=company_id,
            target_date=target_date,
            create_if_missing=create_if_missing,
            created_by=current_user.id if create_if_missing else None
        )
        
        if not period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No accounting period found for date {target_date}"
            )
            
        return period
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Financial Statement endpoints
@router.post(
    "/financial-statements/generate",
    response_model=schemas.FinancialStatementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a financial statement",
    description="Generate a financial statement of the specified type for the given date range.",
    response_description="The generated financial statement",
    tags=["Financial Reports"]
)
async def generate_financial_statement(
    statement_in: schemas.FinancialStatementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a financial statement of the specified type.
    """
    service = get_financial_statement_service(db)
    try:
        return service.generate_financial_statement(
            statement_type=statement_in.statement_type,
            company_id=statement_in.company_id,
            start_date=statement_in.start_date,
            end_date=statement_in.end_date,
            period_id=statement_in.period_id,
            created_by=current_user.id,
            is_final=statement_in.is_final,
            name=statement_in.name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/financial-statements/{statement_id}",
    response_model=schemas.FinancialStatementResponse,
    summary="Get financial statement by ID",
    description="Get detailed information about a specific financial statement.",
    response_description="The requested financial statement",
    tags=["Financial Reports"]
)
async def get_financial_statement(
    statement_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed information about a specific financial statement.
    """
    service = get_financial_statement_service(db)
    statement = service.get(statement_id)
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial statement not found"
        )
    return service._format_statement_response(statement)


@router.get(
    "/financial-statements/company/{company_id}",
    response_model=List[schemas.FinancialStatementResponse],
    summary="List financial statements for a company",
    description="List all financial statements for a specific company with optional filtering.",
    response_description="List of financial statements",
    tags=["Financial Reports"]
)
async def list_financial_statements(
    company_id: UUID,
    statement_type: Optional[schemas.FinancialStatementType] = None,
    is_final: Optional[bool] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List financial statements for a company with optional filtering.
    """
    service = get_financial_statement_service(db)
    query = db.query(FinancialStatement).filter(
        FinancialStatement.company_id == company_id
    )
    
    if statement_type:
        query = query.filter(FinancialStatement.statement_type == statement_type)
    
    if is_final is not None:
        query = query.filter(FinancialStatement.is_final == is_final)
    
    if start_date:
        query = query.filter(FinancialStatement.end_date >= start_date)
    
    if end_date:
        query = query.filter(FinancialStatement.start_date <= end_date)
    
    statements = query.order_by(FinancialStatement.end_date.desc())\
                     .offset(skip).limit(limit).all()
    
    return [service._format_statement_response(stmt) for stmt in statements]


@router.post(
    "/financial-statements/{statement_id}/finalize",
    response_model=schemas.FinancialStatementResponse,
    summary="Finalize a financial statement",
    description="Mark a financial statement as final (read-only).",
    response_description="The finalized financial statement",
    tags=["Financial Reports"]
)
async def finalize_financial_statement(
    statement_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark a financial statement as final (read-only).
    """
    service = get_financial_statement_service(db)
    statement = service.get(statement_id)
    
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial statement not found"
        )
    
    if statement.is_final:
        return service._format_statement_response(statement)
    
    statement.is_final = True
    statement.updated_at = datetime.utcnow()
    statement.updated_by = current_user.id
    
    db.commit()
    db.refresh(statement)
    
    return service._format_statement_response(statement)


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
