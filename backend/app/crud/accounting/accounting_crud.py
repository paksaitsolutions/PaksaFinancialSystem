"""
CRUD operations for accounting.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.accounting import AccountingChartOfAccountsMain, JournalEntry, JournalEntryLine, AccountingRule
from app.models.financial_core import FinancialPeriod
from app.models.base import BaseModel
from app.schemas.accounting.accounting_schemas import (
    ChartOfAccountsCreate, ChartOfAccountsUpdate,
    JournalEntryCreate, JournalEntryUpdate,
    FinancialPeriodCreate, AccountingRuleCreate
)

class AccountingCRUD:
    """CRUD operations for accounting."""
    
    def __init__(self):
        self.coa_helper = QueryHelper(AccountingChartOfAccountsMain)
        self.journal_helper = QueryHelper(JournalEntry)
    
    # Chart of Accounts
    async def create_account(
        self, 
        db: AsyncSession, 
        *, 
        tenant_id: UUID, 
        obj_in: ChartOfAccountsCreate
    ) -> AccountingChartOfAccountsMain:
        """Create chart of accounts entry."""
        # Calculate level based on parent
        level = 1
        if obj_in.parent_id:
            parent = await self.get_account(db, tenant_id=tenant_id, id=obj_in.parent_id)
            if parent:
                level = parent.level + 1
        
        account = AccountingChartOfAccountsMain(
            tenant_id=tenant_id,
            level=level,
            **obj_in.dict()
        )
        
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account
    
    async def get_account(self, db: AsyncSession, *, tenant_id: UUID, id: UUID) -> Optional[AccountingChartOfAccountsMain]:
        """Get account by ID."""
        query = select(AccountingChartOfAccountsMain).where(
            and_(AccountingChartOfAccountsMain.id == id, AccountingChartOfAccountsMain.tenant_id == tenant_id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_chart_of_accounts(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        active_only: bool = True
    ) -> List[AccountingChartOfAccountsMain]:
        """Get chart of accounts for tenant."""
        filters = {"tenant_id": tenant_id}
        if active_only:
            filters["is_active"] = True
        
        query = self.coa_helper.build_query(
            filters=filters,
            sort_by="account_code",
            sort_order="asc"
        )
        return await self.coa_helper.execute_query(db, query)
    
    async def setup_default_accounts(self, db: AsyncSession, *, tenant_id: UUID):
        """Setup default chart of accounts for new tenant."""
        default_accounts = [
            # Assets
            {"account_code": "1000", "account_name": "Cash", "account_type": "asset"},
            {"account_code": "1100", "account_name": "Accounts Receivable", "account_type": "asset"},
            {"account_code": "1200", "account_name": "Inventory", "account_type": "asset"},
            {"account_code": "1500", "account_name": "Fixed Assets", "account_type": "asset"},
            
            # Liabilities
            {"account_code": "2000", "account_name": "Accounts Payable", "account_type": "liability"},
            {"account_code": "2100", "account_name": "Accrued Expenses", "account_type": "liability"},
            {"account_code": "2500", "account_name": "Long-term Debt", "account_type": "liability"},
            
            # Equity
            {"account_code": "3000", "account_name": "Owner's Equity", "account_type": "equity"},
            {"account_code": "3100", "account_name": "Retained Earnings", "account_type": "equity"},
            
            # Revenue
            {"account_code": "4000", "account_name": "Sales Revenue", "account_type": "revenue"},
            {"account_code": "4100", "account_name": "Service Revenue", "account_type": "revenue"},
            
            # Expenses
            {"account_code": "5000", "account_name": "Cost of Goods Sold", "account_type": "expense"},
            {"account_code": "6000", "account_name": "Operating Expenses", "account_type": "expense"},
            {"account_code": "6100", "account_name": "Salaries Expense", "account_type": "expense"},
        ]
        
        for account_data in default_accounts:
            account = AccountingChartOfAccountsMain(
                tenant_id=tenant_id,
                is_system=True,
                **account_data
            )
            db.add(account)
        
        await db.commit()
    
    # Journal Entries
    async def create_journal_entry(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        obj_in: JournalEntryCreate
    ) -> JournalEntry:
        """Create journal entry with lines."""
        # Validate double-entry
        total_debits = sum(line.debit_amount for line in obj_in.lines)
        total_credits = sum(line.credit_amount for line in obj_in.lines)
        
        if total_debits != total_credits:
            raise ValueError("Debits must equal credits")
        
        # Generate entry number
        entry_number = await self._generate_entry_number(db, tenant_id)
        
        # Create journal entry
        entry_data = obj_in.dict(exclude={"lines"})
        journal_entry = JournalEntry(
            tenant_id=tenant_id,
            entry_number=entry_number,
            **entry_data
        )
        
        db.add(journal_entry)
        await db.flush()
        
        # Create lines
        for line_data in obj_in.lines:
            line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                debit_amount_base=line_data.debit_amount * obj_in.exchange_rate,
                credit_amount_base=line_data.credit_amount * obj_in.exchange_rate,
                **line_data.dict()
            )
            db.add(line)
        
        await db.commit()
        await db.refresh(journal_entry)
        return journal_entry
    
    async def get_journal_entries(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[JournalEntry]:
        """Get journal entries for tenant."""
        base_filters = {"tenant_id": tenant_id}
        if filters:
            base_filters.update(filters)
        
        query = self.journal_helper.build_query(
            filters=base_filters,
            sort_by="entry_date",
            sort_order="desc",
            skip=skip,
            limit=limit,
            eager_load=["lines"]
        )
        return await self.journal_helper.execute_query(db, query)
    
    async def post_journal_entry(
        self,
        db: AsyncSession,
        *,
        journal_entry: JournalEntry,
        posted_by: UUID
    ) -> JournalEntry:
        """Post journal entry."""
        if journal_entry.status != "draft":
            raise ValueError("Only draft entries can be posted")
        
        journal_entry.status = "posted"
        journal_entry.posted_at = datetime.utcnow()
        journal_entry.posted_by = posted_by
        journal_entry.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(journal_entry)
        return journal_entry
    
    # Financial Periods
    async def create_financial_period(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        obj_in: FinancialPeriodCreate
    ) -> FinancialPeriod:
        """Create financial period."""
        # If this is current period, unset others
        if obj_in.is_current:
            await self._unset_current_periods(db, tenant_id)
        
        period = FinancialPeriod(
            tenant_id=tenant_id,
            **obj_in.dict()
        )
        
        db.add(period)
        await db.commit()
        await db.refresh(period)
        return period
    
    async def close_financial_period(
        self,
        db: AsyncSession,
        *,
        period: FinancialPeriod
    ) -> FinancialPeriod:
        """Close financial period."""
        period.is_closed = True
        period.closed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(period)
        return period
    
    # Accounting Rules
    async def create_accounting_rule(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        obj_in: AccountingRuleCreate
    ) -> AccountingRule:
        """Create accounting rule."""
        rule = AccountingRule(
            tenant_id=tenant_id,
            **obj_in.dict()
        )
        
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule
    
    async def apply_accounting_rules(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        trigger_event: str,
        event_data: Dict[str, Any]
    ) -> List[JournalEntry]:
        """Apply accounting rules for an event."""
        # Get active rules for trigger event
        query = select(AccountingRule).where(
            and_(
                AccountingRule.tenant_id == tenant_id,
                AccountingRule.trigger_event == trigger_event,
                AccountingRule.is_active == True
            )
        )
        result = await db.execute(query)
        rules = result.scalars().all()
        
        created_entries = []
        
        for rule in rules:
            # Simple rule application - in real implementation, evaluate conditions
            if self._evaluate_rule_conditions(rule.conditions, event_data):
                # Create journal entry based on rule
                entry_data = JournalEntryCreate(
                    entry_date=datetime.utcnow(),
                    description=f"Auto: {rule.rule_name}",
                    reference=event_data.get("reference", ""),
                    lines=[
                        {
                            "account_id": rule.debit_account_id,
                            "debit_amount": event_data.get("amount", 0),
                            "credit_amount": 0,
                            "description": f"Auto debit: {rule.rule_name}"
                        },
                        {
                            "account_id": rule.credit_account_id,
                            "debit_amount": 0,
                            "credit_amount": event_data.get("amount", 0),
                            "description": f"Auto credit: {rule.rule_name}"
                        }
                    ]
                )
                
                entry = await self.create_journal_entry(
                    db, tenant_id=tenant_id, obj_in=entry_data
                )
                created_entries.append(entry)
        
        return created_entries
    
    async def _generate_entry_number(self, db: AsyncSession, tenant_id: UUID) -> str:
        """Generate journal entry number."""
        query = select(func.count()).select_from(JournalEntry).where(
            JournalEntry.tenant_id == tenant_id
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        return f"JE-{count + 1:06d}"
    
    async def _unset_current_periods(self, db: AsyncSession, tenant_id: UUID):
        """Unset current flag from other periods."""
        query = select(FinancialPeriod).where(
            and_(
                FinancialPeriod.tenant_id == tenant_id,
                FinancialPeriod.is_current == True
            )
        )
        result = await db.execute(query)
        periods = result.scalars().all()
        
        for period in periods:
            period.is_current = False
    
    def _evaluate_rule_conditions(self, conditions: str, event_data: Dict[str, Any]) -> bool:
        """Evaluate rule conditions (simplified)."""
        # In real implementation, parse JSON conditions and evaluate
        return True

# Create instance
accounting_crud = AccountingCRUD()