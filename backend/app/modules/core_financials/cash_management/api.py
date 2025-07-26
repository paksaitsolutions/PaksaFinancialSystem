from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
from app.core.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from .services.cash_flow_service import CashFlowService
from .services.bank_reconciliation_service import BankReconciliationService

router = APIRouter()

@router.get('/cash-flow/forecast')
async def get_cash_flow_forecast(
    start_date: date = Query(...),
    end_date: date = Query(...),
    account_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get cash flow forecast from real data"""
    cash_flow_service = CashFlowService()
    forecast = await cash_flow_service.get_cash_flow_forecast(db, start_date, end_date, account_id)
    return forecast

@router.get('/cash-position')
async def get_cash_position(
    as_of_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current cash position from real account data"""
    from .services import CashManagementService
    cash_service = CashManagementService()
    position = await cash_service.get_cash_position(db, as_of_date)
    return position

@router.post('/payments')
async def process_payment(
    payment_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process payment transaction with real database persistence"""
    from .services import CashManagementService
    cash_service = CashManagementService()
    result = await cash_service.process_payment(db, payment_data, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post('/reconciliation/{reconciliation_id}/auto-reconcile')
async def auto_reconcile(
    reconciliation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform automatic reconciliation with real matching logic"""
    recon_service = BankReconciliationService()
    result = await recon_service.auto_reconcile(db, reconciliation_id, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post('/reconciliation')
async def create_reconciliation(
    recon_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bank reconciliation"""
    recon_service = BankReconciliationService()
    result = await recon_service.create_reconciliation(db, recon_data, current_user.id)
    return result

@router.get('/reconciliation/status/{account_id}')
async def get_reconciliation_status(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reconciliation status for an account"""
    recon_service = BankReconciliationService()
    status = await recon_service.get_reconciliation_status(db, account_id)
    return status

@router.post('/bank-accounts/{account_id}/import-statement')
async def import_bank_statement(
    account_id: int,
    statement_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import bank statement data with real processing"""
    from .services import BankAccountService
    bank_service = BankAccountService()
    result = await bank_service.import_bank_statement(db, account_id, statement_data, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get('/banking-fees')
async def get_banking_fees(
    account_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get banking fees from real data"""
    from .services import BankAccountService
    bank_service = BankAccountService()
    fees = await bank_service.get_banking_fees(db, account_id, start_date, end_date)
    return fees

@router.post('/banking-fees')
async def create_banking_fee(
    fee_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create banking fee record with real database persistence"""
    from .services import BankAccountService
    bank_service = BankAccountService()
    result = await bank_service.create_banking_fee(db, fee_data, current_user.id)
    return result