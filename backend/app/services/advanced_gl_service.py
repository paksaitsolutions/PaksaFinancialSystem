"""
Advanced General Ledger Service with enterprise features.
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple

from decimal import Decimal
from sqlalchemy import and_, or_, func, select
from sqlalchemy.orm import Session

from app.core.audit import AuditLogger, AuditAction, AuditLevel
from app.core.exceptions import ValidationException, NotFoundException
from app.core.permissions import Permission, has_permission
from app.models.gl_models import (
from app.models.user import User

    ChartOfAccounts, JournalEntry, JournalEntryLine,
    AccountingPeriod, LedgerBalance, TrialBalance
)


class AdvancedGLService:
    """Advanced General Ledger service with enterprise features."""
    
    def __init__(self, db: Session, user: User, company_id: str):
        self.db = db
        self.user = user
        self.company_id = company_id
        self.audit_logger = AuditLogger(db)
    
    async def create_journal_entry(
        self,
        entry_data: Dict[str, Any],
        auto_post: bool = False
    ) -> JournalEntry:
        """Create Journal Entry."""
        """Create Journal Entry."""
        """Create journal entry with validation and audit trail."""
        
        # Validate permissions
        if not has_permission(self.user, Permission.GL_WRITE):
            raise ValidationException("Insufficient permissions to create journal entries")
        
        # Validate entry data
        self._validate_journal_entry(entry_data)
        
        # Create journal entry
        entry = JournalEntry(
            company_id=self.company_id,
            entry_number=await self._generate_entry_number(),
            entry_date=entry_data["entry_date"],
            description=entry_data["description"],
            reference=entry_data.get("reference"),
            created_by=str(self.user.id),
            status="draft"
        )
        
        self.db.add(entry)
        self.db.flush()
        
        # Create journal entry lines
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for line_data in entry_data["lines"]:
            line = JournalEntryLine(
                journal_entry_id=entry.id,
                account_id=line_data["account_id"],
                description=line_data.get("description", entry_data["description"]),
                debit_amount=Decimal(str(line_data.get("debit_amount", 0))),
                credit_amount=Decimal(str(line_data.get("credit_amount", 0))),
                reference=line_data.get("reference")
            )
            
            total_debits += line.debit_amount
            total_credits += line.credit_amount
            
            self.db.add(line)
        
        # Validate balanced entry
        if total_debits != total_credits:
            raise ValidationException(
                f"Journal entry is not balanced. Debits: {total_debits}, Credits: {total_credits}"
            )
        
        entry.total_amount = total_debits
        
        # Auto-post if requested and user has permission
        if auto_post and has_permission(self.user, Permission.GL_POST):
            await self._post_journal_entry(entry)
        
        self.db.commit()
        
        # Audit log
        self.audit_logger.log_create(
            resource_type="JournalEntry",
            resource_id=str(entry.id),
            new_values={
                "entry_number": entry.entry_number,
                "amount": float(entry.total_amount),
                "description": entry.description
            },
            user_id=str(self.user.id),
            company_id=self.company_id
        )
        
        return entry
    
    async def post_journal_entry(self, entry_id: str) -> JournalEntry:
        
        if not has_permission(self.user, Permission.GL_POST):
            raise ValidationException("Insufficient permissions to post journal entries")
        
        entry = self.db.query(JournalEntry).filter(
            JournalEntry.id == entry_id,
            JournalEntry.company_id == self.company_id
        ).first()
        
        if not entry:
            raise NotFoundException("Journal entry not found")
        
        if entry.status == "posted":
            raise ValidationException("Journal entry is already posted")
        
        await self._post_journal_entry(entry)
        self.db.commit()
        
        # Audit log
        self.audit_logger.log(
            action=AuditAction.APPROVE,
            resource_type="JournalEntry",
            resource_id=str(entry.id),
            user_id=str(self.user.id),
            level=AuditLevel.HIGH,
            message=f"Posted journal entry {entry.entry_number}",
            company_id=self.company_id
        )
        
        return entry
    
    async def _post_journal_entry(self, entry: JournalEntry):
        
        # Update account balances
        for line in entry.lines:
            account = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.id == line.account_id
            ).first()
            
            if not account:
                continue
            
            # Update account balance based on account type
            if account.account_type in ["Asset", "Expense"]:
                # Debit increases, Credit decreases
                account.balance += line.debit_amount - line.credit_amount
            else:
                # Credit increases, Debit decreases (Liability, Equity, Revenue)
                account.balance += line.credit_amount - line.debit_amount
            
            # Create or update ledger balance
            ledger_balance = self.db.query(LedgerBalance).filter(
                and_(
                    LedgerBalance.account_id == account.id,
                    LedgerBalance.period_year == entry.entry_date.year,
                    LedgerBalance.period_month == entry.entry_date.month
                )
            ).first()
            
            if not ledger_balance:
                ledger_balance = LedgerBalance(
                    account_id=account.id,
                    period_year=entry.entry_date.year,
                    period_month=entry.entry_date.month,
                    opening_balance=Decimal('0'),
                    debit_total=Decimal('0'),
                    credit_total=Decimal('0'),
                    closing_balance=Decimal('0')
                )
                self.db.add(ledger_balance)
            
            ledger_balance.debit_total += line.debit_amount
            ledger_balance.credit_total += line.credit_amount
            
            # Calculate closing balance
            if account.account_type in ["Asset", "Expense"]:
                ledger_balance.closing_balance = (
                    ledger_balance.opening_balance + 
                    ledger_balance.debit_total - 
                    ledger_balance.credit_total
                )
            else:
                ledger_balance.closing_balance = (
                    ledger_balance.opening_balance + 
                    ledger_balance.credit_total - 
                    ledger_balance.debit_total
                )
        
        # Update entry status
        entry.status = "posted"
        entry.posted_at = datetime.utcnow()
        entry.posted_by = str(self.user.id)
    
    async def generate_trial_balance(
        self,
        as_of_date: date,
        include_zero_balances: bool = False
    ) -> Dict[str, Any]:
        """Generate Trial Balance."""
        """Generate Trial Balance."""
        """Generate trial balance report."""
        
        if not has_permission(self.user, Permission.REPORTS_GENERATE):
            raise ValidationException("Insufficient permissions to generate reports")
        
        # Get all accounts with balances
        accounts_query = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == self.company_id,
            ChartOfAccounts.is_active == True
        )
        
        if not include_zero_balances:
            accounts_query = accounts_query.filter(ChartOfAccounts.balance != 0)
        
        accounts = accounts_query.order_by(ChartOfAccounts.account_code).all()
        
        trial_balance_entries = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for account in accounts:
            # Calculate balance as of date
            balance = await self._calculate_account_balance(account.id, as_of_date)
            
            if balance == 0 and not include_zero_balances:
                continue
            
            debit_amount = balance if balance > 0 else Decimal('0')
            credit_amount = abs(balance) if balance < 0 else Decimal('0')
            
            # For normal credit accounts, show positive balance as credit
            if account.account_type in ["Liability", "Equity", "Revenue"] and balance > 0:
                debit_amount = Decimal('0')
                credit_amount = balance
            
            trial_balance_entries.append({
                "account_id": str(account.id),
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "debit_amount": float(debit_amount),
                "credit_amount": float(credit_amount),
                "balance": float(balance)
            })
            
            total_debits += debit_amount
            total_credits += credit_amount
        
        # Create trial balance record
        trial_balance = TrialBalance(
            company_id=self.company_id,
            as_of_date=as_of_date,
            total_debits=total_debits,
            total_credits=total_credits,
            is_balanced=abs(total_debits - total_credits) < Decimal('0.01'),
            created_by=str(self.user.id)
        )
        
        self.db.add(trial_balance)
        self.db.commit()
        
        # Audit log
        self.audit_logger.log(
            action=AuditAction.CREATE,
            resource_type="TrialBalance",
            resource_id=str(trial_balance.id),
            user_id=str(self.user.id),
            level=AuditLevel.MEDIUM,
            message=f"Generated trial balance as of {as_of_date}",
            metadata={"as_of_date": as_of_date.isoformat()},
            company_id=self.company_id
        )
        
        return {
            "trial_balance_id": str(trial_balance.id),
            "as_of_date": as_of_date.isoformat(),
            "entries": trial_balance_entries,
            "total_debits": float(total_debits),
            "total_credits": float(total_credits),
            "difference": float(total_debits - total_credits),
            "is_balanced": trial_balance.is_balanced,
            "generated_at": trial_balance.created_at.isoformat(),
            "generated_by": self.user.email
        }
    
    async def close_accounting_period(
        self,
        period_year: int,
        period_month: int
    ) -> AccountingPeriod:
        """Close Accounting Period."""
        """Close Accounting Period."""
        """Close accounting period with proper validations."""
        
        if not has_permission(self.user, Permission.GL_CLOSE_PERIOD):
            raise ValidationException("Insufficient permissions to close accounting periods")
        
        # Check if period exists
        period = self.db.query(AccountingPeriod).filter(
            and_(
                AccountingPeriod.company_id == self.company_id,
                AccountingPeriod.year == period_year,
                AccountingPeriod.month == period_month
            )
        ).first()
        
        if not period:
            # Create period if it doesn't exist
            period = AccountingPeriod(
                company_id=self.company_id,
                year=period_year,
                month=period_month,
                status="open"
            )
            self.db.add(period)
        
        if period.status == "closed":
            raise ValidationException("Accounting period is already closed")
        
        # Validate all entries are posted
        unposted_entries = self.db.query(JournalEntry).filter(
            and_(
                JournalEntry.company_id == self.company_id,
                func.extract('year', JournalEntry.entry_date) == period_year,
                func.extract('month', JournalEntry.entry_date) == period_month,
                JournalEntry.status != "posted"
            )
        ).count()
        
        if unposted_entries > 0:
            raise ValidationException(
                f"Cannot close period with {unposted_entries} unposted journal entries"
            )
        
        # Close the period
        period.status = "closed"
        period.closed_at = datetime.utcnow()
        period.closed_by = str(self.user.id)
        
        self.db.commit()
        
        # Audit log
        self.audit_logger.log(
            action=AuditAction.CONFIGURE,
            resource_type="AccountingPeriod",
            resource_id=str(period.id),
            user_id=str(self.user.id),
            level=AuditLevel.CRITICAL,
            message=f"Closed accounting period {period_year}-{period_month:02d}",
            metadata={
                "period_year": period_year,
                "period_month": period_month
            },
            company_id=self.company_id
        )
        
        return period
    
    async def _calculate_account_balance(
        self,
        account_id: str,
        as_of_date: date
    ) -> Decimal:
        """Calculate Account Balance."""
        """Calculate Account Balance."""
        """Calculate account balance as of specific date."""
        
        # Get all posted journal entry lines for this account up to the date
        lines = self.db.query(JournalEntryLine).join(JournalEntry).filter(
            and_(
                JournalEntryLine.account_id == account_id,
                JournalEntry.entry_date <= as_of_date,
                JournalEntry.status == "posted",
                JournalEntry.company_id == self.company_id
            )
        ).all()
        
        total_debits = sum(line.debit_amount for line in lines)
        total_credits = sum(line.credit_amount for line in lines)
        
        # Get account to determine normal balance
        account = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == account_id
        ).first()
        
        if not account:
            return Decimal('0')
        
        # Calculate balance based on account type
        if account.account_type in ["Asset", "Expense"]:
            # Normal debit balance
            return total_debits - total_credits
        else:
            # Normal credit balance (Liability, Equity, Revenue)
            return total_credits - total_debits
    
    def _validate_journal_entry(self, entry_data: Dict[str, Any]):
        
        if not entry_data.get("entry_date"):
            raise ValidationException("Entry date is required")
        
        if not entry_data.get("description"):
            raise ValidationException("Description is required")
        
        if not entry_data.get("lines") or len(entry_data["lines"]) < 2:
            raise ValidationException("At least two journal entry lines are required")
        
        # Validate each line
        for i, line in enumerate(entry_data["lines"]):
            if not line.get("account_id"):
                raise ValidationException(f"Account ID is required for line {i+1}")
            
            debit = Decimal(str(line.get("debit_amount", 0)))
            credit = Decimal(str(line.get("credit_amount", 0)))
            
            if debit == 0 and credit == 0:
                raise ValidationException(f"Either debit or credit amount is required for line {i+1}")
            
            if debit > 0 and credit > 0:
                raise ValidationException(f"Line {i+1} cannot have both debit and credit amounts")
    
    async def _generate_entry_number(self) -> str:
        
        today = datetime.now().date()
        year = today.year
        month = today.month
        
        # Count entries for this month
        count = self.db.query(JournalEntry).filter(
            and_(
                JournalEntry.company_id == self.company_id,
                func.extract('year', JournalEntry.entry_date) == year,
                func.extract('month', JournalEntry.entry_date) == month
            )
        ).count()
        
        return f"JE-{year}{month:02d}-{count+1:04d}"