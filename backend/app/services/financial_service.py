"""
Enhanced Financial Services with double-entry validation and business logic
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from decimal import Decimal
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
import uuid

from app.core.auth_enhanced import get_current_user
from app.models.financial_core import *
from app.schemas.financial_schemas import *


class FinancialService:
    def __init__(self, db: Session):
        self.db = db

    def create_journal_entry(self, entry_data: JournalEntryCreate, user_id: str) -> JournalEntry:
        # Generate entry number
        entry_number = self._generate_entry_number()
        
        # Calculate totals
        total_debit = sum(line.debit_amount for line in entry_data.lines)
        total_credit = sum(line.credit_amount for line in entry_data.lines)
        
        # Create journal entry
        journal_entry = JournalEntry(
            entry_number=entry_number,
            description=entry_data.description,
            reference=entry_data.reference,
            entry_date=entry_data.entry_date,
            total_debit=total_debit,
            total_credit=total_credit,
            created_by=user_id,
            status='draft'
        )
        
        # Validate balanced entry
        journal_entry.validate_balanced_entry()
        
        self.db.add(journal_entry)
        self.db.flush()
        
        # Create journal entry lines
        for i, line_data in enumerate(entry_data.lines, 1):
            line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=line_data.account_id,
                description=line_data.description,
                debit_amount=line_data.debit_amount,
                credit_amount=line_data.credit_amount,
                line_number=i
            )
            line.validate_debit_credit_exclusive()
            self.db.add(line)
        
        self.db.commit()
        return journal_entry

    def post_journal_entry(self, entry_id: str, user_id: str) -> JournalEntry:
        entry = self.db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            raise ValueError("Journal entry not found")
        
        if entry.status != 'approved':
            raise ValueError("Journal entry must be approved before posting")
        
        # Update account balances
        for line in entry.lines:
            account = self.db.query(ChartOfAccounts).filter(ChartOfAccounts.id == line.account_id).first()
            if account:
                if account.normal_balance == 'Debit':
                    account.current_balance += line.debit_amount - line.credit_amount
                else:
                    account.current_balance += line.credit_amount - line.debit_amount
        
        # Update entry status
        entry.status = 'posted'
        entry.posted_by = user_id
        entry.posted_at = datetime.utcnow()
        
        self.db.commit()
        return entry

    def get_trial_balance(self, as_of_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        if not as_of_date:
            as_of_date = datetime.utcnow()
        
        # Get all accounts with balances
        accounts = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.is_active == True
        ).all()
        
        trial_balance = []
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for account in accounts:
            balance = account.current_balance or Decimal('0')
            
            if account.normal_balance == 'Debit':
                debit_balance = balance if balance > 0 else Decimal('0')
                credit_balance = abs(balance) if balance < 0 else Decimal('0')
            else:
                credit_balance = balance if balance > 0 else Decimal('0')
                debit_balance = abs(balance) if balance < 0 else Decimal('0')
            
            trial_balance.append({
                'account_code': account.account_code,
                'account_name': account.account_name,
                'account_type': account.account_type,
                'debit_balance': debit_balance,
                'credit_balance': credit_balance,
                'balance': balance
            })
            
            total_debit += debit_balance
            total_credit += credit_balance
        
        return {
            'accounts': trial_balance,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'is_balanced': abs(total_debit - total_credit) < Decimal('0.01'),
            'as_of_date': as_of_date
        }

    def generate_financial_statements(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        
        # Balance Sheet
        assets = self._get_accounts_by_type('Asset', period_end)
        liabilities = self._get_accounts_by_type('Liability', period_end)
        equity = self._get_accounts_by_type('Equity', period_end)
        
        total_assets = sum(acc['balance'] for acc in assets)
        total_liabilities = sum(acc['balance'] for acc in liabilities)
        total_equity = sum(acc['balance'] for acc in equity)
        
        # Income Statement
        revenue = self._get_accounts_by_type('Revenue', period_end, period_start)
        expenses = self._get_accounts_by_type('Expense', period_end, period_start)
        
        total_revenue = sum(acc['balance'] for acc in revenue)
        total_expenses = sum(acc['balance'] for acc in expenses)
        net_income = total_revenue - total_expenses
        
        return {
            'balance_sheet': {
                'assets': assets,
                'liabilities': liabilities,
                'equity': equity,
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'total_equity': total_equity,
                'balanced': abs(total_assets - (total_liabilities + total_equity)) < Decimal('0.01')
            },
            'income_statement': {
                'revenue': revenue,
                'expenses': expenses,
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_income': net_income,
                'period_start': period_start,
                'period_end': period_end
            }
        }

    def process_period_close(self, period_end: datetime, user_id: str) -> Dict[str, Any]:
        
        # 1. Validate all journal entries are posted
        unposted_entries = self.db.query(JournalEntry).filter(
            and_(
                JournalEntry.entry_date <= period_end,
                JournalEntry.status != 'posted'
            )
        ).count()
        
        if unposted_entries > 0:
            raise ValueError(f"Cannot close period: {unposted_entries} unposted journal entries")
        
        # 2. Generate closing entries for revenue and expense accounts
        revenue_accounts = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Revenue'
        ).all()
        
        expense_accounts = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Expense'
        ).all()
        
        # Create closing entries
        closing_entries = []
        
        # Close revenue accounts
        for account in revenue_accounts:
            if account.current_balance > 0:
                closing_entries.append({
                    'account_id': account.id,
                    'debit_amount': account.current_balance,
                    'credit_amount': Decimal('0'),
                    'description': f'Close {account.account_name}'
                })
        
        # Close expense accounts
        for account in expense_accounts:
            if account.current_balance > 0:
                closing_entries.append({
                    'account_id': account.id,
                    'debit_amount': Decimal('0'),
                    'credit_amount': account.current_balance,
                    'description': f'Close {account.account_name}'
                })
        
        # Create retained earnings entry
        net_income = sum(acc.current_balance for acc in revenue_accounts) - sum(acc.current_balance for acc in expense_accounts)
        
        if closing_entries:
            # Find or create retained earnings account
            retained_earnings = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.account_code == '3000'
            ).first()
            
            if not retained_earnings:
                retained_earnings = ChartOfAccounts(
                    account_code='3000',
                    account_name='Retained Earnings',
                    account_type='Equity',
                    normal_balance='Credit',
                    is_system_account=True
                )
                self.db.add(retained_earnings)
                self.db.flush()
            
            closing_entries.append({
                'account_id': retained_earnings.id,
                'debit_amount': Decimal('0') if net_income > 0 else abs(net_income),
                'credit_amount': net_income if net_income > 0 else Decimal('0'),
                'description': 'Transfer net income to retained earnings'
            })
            
            # Create closing journal entry
            closing_je = JournalEntryCreate(
                description=f'Period closing entries for {period_end.strftime("%Y-%m-%d")}',
                entry_date=period_end,
                lines=closing_entries
            )
            
            journal_entry = self.create_journal_entry(closing_je, user_id)
            
            # Auto-approve and post closing entry
            journal_entry.status = 'approved'
            journal_entry.approved_by = user_id
            journal_entry.approved_at = datetime.utcnow()
            
            self.post_journal_entry(journal_entry.id, user_id)
        
        return {
            'period_end': period_end,
            'net_income': net_income,
            'closing_entry_id': journal_entry.id if closing_entries else None,
            'message': 'Period closed successfully'
        }

    def _generate_entry_number(self) -> str:
        today = datetime.now()
        prefix = f"JE{today.strftime('%Y%m')}"
        
        last_entry = self.db.query(JournalEntry).filter(
            JournalEntry.entry_number.like(f"{prefix}%")
        ).order_by(JournalEntry.entry_number.desc()).first()
        
        if last_entry:
            last_num = int(last_entry.entry_number[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"

    def _get_accounts_by_type(self, account_type: str, as_of_date: datetime, from_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        accounts = self.db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.account_type == account_type,
                ChartOfAccounts.is_active == True
            )
        ).all()
        
        result = []
        for account in accounts:
            balance = account.current_balance or Decimal('0')
            result.append({
                'account_code': account.account_code,
                'account_name': account.account_name,
                'balance': balance
            })
        
        return result