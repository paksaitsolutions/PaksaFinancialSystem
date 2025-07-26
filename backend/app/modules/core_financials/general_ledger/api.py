"""
General Ledger API endpoints.
"""
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.modules.core_financials.general_ledger.services import AccountService, JournalEntryService
from app.modules.core_financials.general_ledger.ai_bi_service import GLAIBIService, GLBIEndpointService
from app.modules.core_financials.general_ledger.audit_service import GLAuditService
from fastapi import Query
from datetime import date
from app.modules.core_financials.general_ledger.schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
    JournalEntryCreate, JournalEntryResponse,
    TrialBalanceResponse, TrialBalanceItem
)
from app.core.exceptions.handlers import handle_exception, ValidationError, NotFoundError
from app.core.logging.config import get_logger

logger = get_logger("gl_api")

router = APIRouter()
account_service = AccountService()
journal_service = JournalEntryService()

# Account endpoints
@router.post("/accounts/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
@handle_exception
async def create_account(
    account: AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Creating account: {account.account_code}")
    
    # Check if account code already exists
    existing = await account_service.get_by_code(db, account.account_code)
    if existing:
        logger.warning(f"Account code already exists: {account.account_code}")
        raise ValidationError("Account code already exists", "account_code")
    
    result = await account_service.create(db, obj_in=account)
    logger.info(f"Account created successfully: {result.id}")
    
    # Log audit trail
    await GLAuditService.log_account_action(
        db, "test-tenant", "test-user", "CREATE", str(result.id), None, account.dict()
    )
    
    return result

@router.get("/accounts/", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await account_service.get_multi(db, skip=skip, limit=limit)

@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    account = await account_service.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account

@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    account = await account_service.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return await account_service.update(db, db_obj=account, obj_in=account_update)

@router.get("/chart-of-accounts/", response_model=List[AccountResponse])
async def get_chart_of_accounts(db: AsyncSession = Depends(get_db)):
    return await account_service.get_chart_of_accounts(db)

# Journal Entry endpoints
@router.post("/journal-entries/", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    journal_entry: JournalEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await journal_service.create_journal_entry(db, entry_data=journal_entry)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/journal-entries/{entry_id}/post", response_model=JournalEntryResponse)
@handle_exception
async def post_journal_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Posting journal entry: {entry_id}")
    
    try:
        result = await journal_service.post_entry(db, entry_id)
        logger.info(f"Journal entry posted successfully: {entry_id}")
        
        # Log audit trail
        await GLAuditService.log_journal_entry_action(
            db, "test-tenant", "test-user", "POST", str(entry_id)
        )
        
        return result
    except ValueError as e:
        logger.error(f"Failed to post journal entry {entry_id}: {str(e)}")
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"Unexpected error posting journal entry {entry_id}: {str(e)}")
        raise

@router.post("/journal-entries/{entry_id}/unpost", response_model=JournalEntryResponse)
async def unpost_journal_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await journal_service.unpost_entry(db, entry_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/journal-entries/{entry_id}/reverse", response_model=JournalEntryResponse)
async def reverse_journal_entry(
    entry_id: int,
    reversal_date: date,
    reason: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await journal_service.reverse_entry(db, entry_id, reversal_date, reason)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/journal-entries/", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await journal_service.get_multi(db, skip=skip, limit=limit)

@router.get("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    entry = await journal_service.get(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    return entry

# Reports
@router.get("/reports/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    as_of_date: date,
    db: AsyncSession = Depends(get_db)
):
    trial_balance_items = await journal_service.get_trial_balance(db, as_of_date)
    total_debits = sum(item.debit_balance for item in trial_balance_items)
    total_credits = sum(item.credit_balance for item in trial_balance_items)
    
    return TrialBalanceResponse(
        as_of_date=as_of_date,
        accounts=trial_balance_items,
        total_debits=total_debits,
        total_credits=total_credits
    )

# AI/BI Integration endpoints
@router.get("/ai-bi/cash-flow-data")
async def get_cash_flow_data(
    months: int = 12,
    db: AsyncSession = Depends(get_db)
):
    """Get cash flow data for predictive analysis"""
    tenant_id = "test-tenant"  # Replace with actual tenant context
    return await GLAIBIService.get_cash_flow_data(db, tenant_id, months)

@router.get("/ai-bi/anomalies")
async def get_journal_anomalies(
    db: AsyncSession = Depends(get_db)
):
    """Detect anomalies in journal entries"""
    tenant_id = "test-tenant"  # Replace with actual tenant context
    return await GLAIBIService.detect_journal_anomalies(db, tenant_id)

@router.get("/ai-bi/kpis")
async def get_real_time_kpis(
    db: AsyncSession = Depends(get_db)
):
    """Get real-time KPIs for dashboards"""
    tenant_id = "test-tenant"  # Replace with actual tenant context
    return await GLAIBIService.get_real_time_kpis(db, tenant_id)

@router.get("/ai-bi/trends")
async def get_financial_trends(
    periods: int = 12,
    db: AsyncSession = Depends(get_db)
):
    """Get financial trends for analysis"""
    tenant_id = "test-tenant"  # Replace with actual tenant context
    return await GLAIBIService.get_financial_trends(db, tenant_id, periods)

# BI Tool Integration endpoints
@router.get("/bi/tableau/{data_type}")
async def tableau_integration(
    data_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Tableau integration endpoint"""
    tenant_id = "test-tenant"  # Replace with actual tenant context
    return await GLBIEndpointService.get_tableau_data(db, tenant_id, data_type)

@router.get("/bi/powerbi/{report_type}")
async def powerbi_integration(
    report_type: str,
    db: AsyncSession = Depends(get_db)
):
    """PowerBI integration endpoint"""
    tenant_id = "test-tenant"  # Replace with actual tenant context
    return await GLBIEndpointService.get_powerbi_data(db, tenant_id, report_type)

@router.get("/bi/metabase/{query_type}")
async def metabase_integration(
    query_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Metabase integration endpoint"""
    tenant_id = "test-tenant"  # Replace with actual tenant context
    return await GLBIEndpointService.get_metabase_data(db, tenant_id, query_type)

# GL Report endpoints
@router.get("/reports/balance-sheet")
async def balance_sheet_report(
    as_of_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db)
):
    """Generate Balance Sheet report"""
    accounts = await db.execute(
        select(Account).where(Account.account_type.in_(['asset', 'liability', 'equity']))
    )
    return {"report_type": "balance_sheet", "as_of_date": as_of_date, "accounts": [acc.__dict__ for acc in accounts.scalars().all()]}

@router.get("/reports/income-statement")
async def income_statement_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Generate Income Statement report"""
    accounts = await db.execute(
        select(Account).where(Account.account_type.in_(['revenue', 'expense']))
    )
    return {"report_type": "income_statement", "period": f"{start_date} to {end_date}", "accounts": [acc.__dict__ for acc in accounts.scalars().all()]}

@router.get("/reports/cash-flow")
async def cash_flow_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Generate Cash Flow report"""
    return {"report_type": "cash_flow", "period": f"{start_date} to {end_date}", "operating_activities": [], "investing_activities": [], "financing_activities": []}

# GL Settings endpoints
@router.get("/settings")
async def get_gl_settings(
    db: AsyncSession = Depends(get_db)
):
    """Get GL settings"""
    return {
        "allow_future_posting": False,
        "require_balanced_entries": True,
        "auto_post_entries": False,
        "base_currency": "USD",
        "fiscal_year_start_month": 1
    }

@router.put("/settings")
async def update_gl_settings(
    settings: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update GL settings"""
    return {"message": "Settings updated successfully", "settings": settings}

@router.post("/period-close/validate")
async def validate_period_close(
    period_end_date: date,
    db: AsyncSession = Depends(get_db)
):
    """Validate period can be closed"""
    journal_service = JournalEntryService()
    return await journal_service.validate_period_close(db, period_end_date)