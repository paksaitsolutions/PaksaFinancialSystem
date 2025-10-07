"""
API endpoints for accounting.
"""
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import select, and_

from app.models.accounting import JournalEntry

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.db.router import db_router
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.crud.accounting.accounting_crud import accounting_crud
from app.schemas.accounting.accounting_schemas import (
    ChartOfAccountsCreate, ChartOfAccountsUpdate, ChartOfAccountsResponse,
    JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse,
    FinancialPeriodCreate, FinancialPeriodResponse,
    AccountingRuleCreate, AccountingRuleResponse
)

router = APIRouter()

# Mock tenant ID
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")

# Chart of Accounts endpoints
@router.post("/chart-of-accounts", response_model=ChartOfAccountsResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    *,
    db: AsyncSession = Depends(get_db),
    account_in: ChartOfAccountsCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create chart of accounts entry."""
    account = await accounting_crud.create_account(
        db, tenant_id=MOCK_TENANT_ID, obj_in=account_in
    )
    return success_response(
        data=account,
        message="Account created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/chart-of-accounts", response_model=List[ChartOfAccountsResponse])
async def get_chart_of_accounts(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    active_only: bool = Query(True),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get chart of accounts."""
    accounts = await accounting_crud.get_chart_of_accounts(
        db, tenant_id=MOCK_TENANT_ID, active_only=active_only
    )
    return success_response(data=accounts)

@router.post("/chart-of-accounts/setup-defaults")
async def setup_default_accounts(
    *,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Setup default chart of accounts."""
    await accounting_crud.setup_default_accounts(db, tenant_id=MOCK_TENANT_ID)
    return success_response(message="Default accounts created successfully")

# Journal Entry endpoints
@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    *,
    db: AsyncSession = Depends(get_db),
    entry_in: JournalEntryCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create journal entry."""
    try:
        entry = await accounting_crud.create_journal_entry(
            db, tenant_id=MOCK_TENANT_ID, obj_in=entry_in
        )
        return success_response(
            data=entry,
            message="Journal entry created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/journal-entries", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get journal entries."""
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    
    entries = await accounting_crud.get_journal_entries(
        db, tenant_id=MOCK_TENANT_ID, skip=skip, limit=limit, filters=filters
    )
    return success_response(data=entries)

@router.post("/journal-entries/{entry_id}/post")
async def post_journal_entry(
    *,
    db: AsyncSession = Depends(get_db),
    entry_id: UUID,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Post journal entry."""
    # Get entry
    query = select(JournalEntry).where(
        and_(JournalEntry.id == entry_id, JournalEntry.tenant_id == MOCK_TENANT_ID)
    )
    result = await db.execute(query)
    entry = result.scalars().first()
    
    if not entry:
        return error_response(
            message="Journal entry not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        # Mock user ID
        posted_by = UUID("12345678-1234-5678-9012-123456789012")
        entry = await accounting_crud.post_journal_entry(
            db, journal_entry=entry, posted_by=posted_by
        )
        return success_response(
            data=entry,
            message="Journal entry posted successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

# Financial Period endpoints
@router.post("/financial-periods", response_model=FinancialPeriodResponse, status_code=status.HTTP_201_CREATED)
async def create_financial_period(
    *,
    db: AsyncSession = Depends(get_db),
    period_in: FinancialPeriodCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create financial period."""
    period = await accounting_crud.create_financial_period(
        db, tenant_id=MOCK_TENANT_ID, obj_in=period_in
    )
    return success_response(
        data=period,
        message="Financial period created successfully",
        status_code=status.HTTP_201_CREATED,
    )

# Accounting Rules endpoints
@router.post("/accounting-rules", response_model=AccountingRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_accounting_rule(
    *,
    db: AsyncSession = Depends(get_db),
    rule_in: AccountingRuleCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create accounting rule."""
    rule = await accounting_crud.create_accounting_rule(
        db, tenant_id=MOCK_TENANT_ID, obj_in=rule_in
    )
    return success_response(
        data=rule,
        message="Accounting rule created successfully",
        status_code=status.HTTP_201_CREATED,
    )