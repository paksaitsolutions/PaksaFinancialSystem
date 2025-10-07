"""
Advanced General Ledger API endpoints with enterprise features.
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import Permission, require_permission
from app.services.advanced_gl_service import AdvancedGLService
from app.models.user import User
from app.core.exceptions import ValidationException, NotFoundException

router = APIRouter()


class JournalEntryLineCreate(BaseModel):
    """Schema for creating journal entry lines."""
    account_id: str
    description: Optional[str] = None
    debit_amount: Optional[float] = 0
    credit_amount: Optional[float] = 0
    reference: Optional[str] = None


class JournalEntryCreate(BaseModel):
    """Schema for creating journal entries."""
    entry_date: date
    description: str
    reference: Optional[str] = None
    lines: List[JournalEntryLineCreate] = Field(..., min_items=2)


class JournalEntryResponse(BaseModel):
    """Schema for journal entry response."""
    id: str
    entry_number: str
    entry_date: date
    description: str
    reference: Optional[str]
    total_amount: float
    status: str
    created_at: datetime
    created_by: str


class TrialBalanceRequest(BaseModel):
    """Schema for trial balance request."""
    as_of_date: date
    include_zero_balances: bool = False


class AccountingPeriodClose(BaseModel):
    """Schema for closing accounting period."""
    period_year: int
    period_month: int


@router.post("/journal-entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    auto_post: bool = Query(False, description="Auto-post entry if user has permission"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new journal entry with validation and audit trail."""
    
    try:
        # Get company_id from user context (simplified for demo)
        company_id = "demo-company-123"
        
        service = AdvancedGLService(db, current_user, company_id)
        entry = await service.create_journal_entry(
            entry_data.dict(),
            auto_post=auto_post
        )
        
        return JournalEntryResponse(
            id=str(entry.id),
            entry_number=entry.entry_number,
            entry_date=entry.entry_date.date(),
            description=entry.description,
            reference=entry.reference,
            total_amount=float(entry.total_amount),
            status=entry.status,
            created_at=entry.created_at,
            created_by=entry.created_by
        )
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create journal entry: {str(e)}"
        )


@router.post("/journal-entries/{entry_id}/post")
async def post_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Post a journal entry to the ledger."""
    
    try:
        company_id = "demo-company-123"
        service = AdvancedGLService(db, current_user, company_id)
        entry = await service.post_journal_entry(entry_id)
        
        return {
            "message": f"Journal entry {entry.entry_number} posted successfully",
            "entry_id": str(entry.id),
            "status": entry.status,
            "posted_at": entry.posted_at
        }
        
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/reports/trial-balance")
async def generate_trial_balance(
    request: TrialBalanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate trial balance report with audit trail."""
    
    try:
        company_id = "demo-company-123"
        service = AdvancedGLService(db, current_user, company_id)
        
        trial_balance = await service.generate_trial_balance(
            as_of_date=request.as_of_date,
            include_zero_balances=request.include_zero_balances
        )
        
        return {
            "success": True,
            "data": trial_balance,
            "message": "Trial balance generated successfully"
        }
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/periods/close")
async def close_accounting_period(
    period_data: AccountingPeriodClose,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close an accounting period with proper validations."""
    
    try:
        company_id = "demo-company-123"
        service = AdvancedGLService(db, current_user, company_id)
        
        period = await service.close_accounting_period(
            period_year=period_data.period_year,
            period_month=period_data.period_month
        )
        
        return {
            "message": f"Accounting period {period_data.period_year}-{period_data.period_month:02d} closed successfully",
            "period_id": str(period.id),
            "status": period.status,
            "closed_at": period.closed_at,
            "closed_by": period.closed_by
        }
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get("/accounts/hierarchy")
async def get_account_hierarchy(
    include_inactive: bool = Query(False, description="Include inactive accounts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chart of accounts in hierarchical structure."""
    
    from app.models.gl_models import ChartOfAccounts
    from sqlalchemy import and_
    
    try:
        company_id = "demo-company-123"
        
        # Build query
        query = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id
        )
        
        if not include_inactive:
            query = query.filter(ChartOfAccounts.is_active == True)
        
        accounts = query.order_by(ChartOfAccounts.account_code).all()
        
        # Build hierarchical structure
        account_dict = {}
        root_accounts = []
        
        # First pass: create account dictionary
        for account in accounts:
            account_dict[str(account.id)] = {
                "id": str(account.id),
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "account_subtype": account.account_subtype,
                "parent_account_id": str(account.parent_account_id) if account.parent_account_id else None,
                "level": account.level,
                "is_header": account.is_header,
                "is_active": account.is_active,
                "balance": float(account.balance),
                "children": []
            }
        
        # Second pass: build hierarchy
        for account_data in account_dict.values():
            if account_data["parent_account_id"] and account_data["parent_account_id"] in account_dict:
                account_dict[account_data["parent_account_id"]]["children"].append(account_data)
            else:
                root_accounts.append(account_data)
        
        return {
            "success": True,
            "data": {
                "accounts": root_accounts,
                "total_accounts": len(accounts)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve account hierarchy: {str(e)}"
        )


@router.get("/reports/financial-position")
async def get_financial_position(
    as_of_date: date = Query(..., description="As of date for the report"),
    comparative_date: Optional[date] = Query(None, description="Comparative period date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate financial position (balance sheet) report."""
    
    from app.models.gl_models import ChartOfAccounts
    from sqlalchemy import and_
    
    try:
        company_id = "demo-company-123"
        service = AdvancedGLService(db, current_user, company_id)
        
        # Get accounts by type
        asset_accounts = db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.account_type == "Asset",
                ChartOfAccounts.is_active == True
            )
        ).order_by(ChartOfAccounts.account_code).all()
        
        liability_accounts = db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.account_type == "Liability",
                ChartOfAccounts.is_active == True
            )
        ).order_by(ChartOfAccounts.account_code).all()
        
        equity_accounts = db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.account_type == "Equity",
                ChartOfAccounts.is_active == True
            )
        ).order_by(ChartOfAccounts.account_code).all()
        
        # Calculate balances
        assets = []
        total_assets = 0
        
        for account in asset_accounts:
            balance = await service._calculate_account_balance(str(account.id), as_of_date)
            comparative_balance = None
            
            if comparative_date:
                comparative_balance = await service._calculate_account_balance(str(account.id), comparative_date)
            
            assets.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_subtype": account.account_subtype,
                "balance": float(balance),
                "comparative_balance": float(comparative_balance) if comparative_balance else None
            })
            total_assets += float(balance)
        
        liabilities = []
        total_liabilities = 0
        
        for account in liability_accounts:
            balance = await service._calculate_account_balance(str(account.id), as_of_date)
            comparative_balance = None
            
            if comparative_date:
                comparative_balance = await service._calculate_account_balance(str(account.id), comparative_date)
            
            liabilities.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_subtype": account.account_subtype,
                "balance": float(balance),
                "comparative_balance": float(comparative_balance) if comparative_balance else None
            })
            total_liabilities += float(balance)
        
        equity = []
        total_equity = 0
        
        for account in equity_accounts:
            balance = await service._calculate_account_balance(str(account.id), as_of_date)
            comparative_balance = None
            
            if comparative_date:
                comparative_balance = await service._calculate_account_balance(str(account.id), comparative_date)
            
            equity.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_subtype": account.account_subtype,
                "balance": float(balance),
                "comparative_balance": float(comparative_balance) if comparative_balance else None
            })
            total_equity += float(balance)
        
        return {
            "success": True,
            "data": {
                "report_name": "Statement of Financial Position",
                "as_of_date": as_of_date.isoformat(),
                "comparative_date": comparative_date.isoformat() if comparative_date else None,
                "assets": {
                    "accounts": assets,
                    "total": total_assets
                },
                "liabilities": {
                    "accounts": liabilities,
                    "total": total_liabilities
                },
                "equity": {
                    "accounts": equity,
                    "total": total_equity
                },
                "total_liabilities_and_equity": total_liabilities + total_equity,
                "is_balanced": abs(total_assets - (total_liabilities + total_equity)) < 0.01
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial position report: {str(e)}"
        )