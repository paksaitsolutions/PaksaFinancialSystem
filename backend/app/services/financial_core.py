"""
Financial Core Services - Double-Entry, Period Closing, Multi-Currency, Tax, Reconciliation
"""
from datetime import datetime, date
from typing import List, Dict, Optional

from decimal import Decimal
from sqlalchemy import and_, func, text
from sqlalchemy.orm import Session
import uuid

from app.models.base import AuditLog
from app.models.financial_core import *


class DoubleEntryService:
    """Service for double-entry accounting validation and operations"""
    
    @staticmethod
    def validate_journal_entry(lines: List[dict]) -> bool:
        """Validate Journal Entry."""
        """Validate that journal entry is balanced"""
        total_debit = sum(Decimal(str(line.get('debit_amount', 0))) for line in lines)
        total_credit = sum(Decimal(str(line.get('credit_amount', 0))) for line in lines)
        return abs(total_debit - total_credit) <= Decimal('0.01')
    
    @staticmethod
    def create_journal_entry(db: Session, entry_data: dict, user_id: str) -> JournalEntry:
        """Create Journal Entry."""
        """Create a balanced journal entry"""
        lines = entry_data.pop('lines', [])
        
        # Validate balanced entry
        if not DoubleEntryService.validate_journal_entry(lines):
            raise ValueError("Journal entry must be balanced (debits = credits)")
        
        # Calculate totals
        total_debit = sum(Decimal(str(line.get('debit_amount', 0))) for line in lines)
        total_credit = sum(Decimal(str(line.get('credit_amount', 0))) for line in lines)
        
        # Create journal entry
        entry = JournalEntry(
            entry_number=f"JE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}",
            total_debit=total_debit,
            total_credit=total_credit,
            created_by=user_id,
            **entry_data
        )
        db.add(entry)
        db.flush()
        
        # Create journal entry lines
        for i, line_data in enumerate(lines, 1):
            line = JournalEntryLine(
                journal_entry_id=entry.id,
                line_number=i,
                **line_data
            )
            db.add(line)
        
        db.commit()
        return entry
    
    @staticmethod
    def post_journal_entry(db: Session, entry_id: str, user_id: str) -> JournalEntry:
        """Post Journal Entry."""
        """Post journal entry and update account balances"""
        entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            raise ValueError("Journal entry not found")
        
        if entry.status != 'approved':
            raise ValueError("Journal entry must be approved before posting")
        
        # Update account balances
        for line in entry.lines:
            account = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == line.account_id).first()
            if account.normal_balance == 'Debit':
                account.current_balance += line.debit_amount - line.credit_amount
            else:
                account.current_balance += line.credit_amount - line.debit_amount
        
        entry.status = 'posted'
        entry.posted_by = user_id
        entry.posted_at = datetime.now()
        
        db.commit()
        return entry

class PeriodClosingService:
    """Service for period closing operations"""
    
    @staticmethod
    def close_period(db: Session, period_end: date, user_id: str) -> dict:
        """Close Period."""
        """Close accounting period"""
        # Check for unposted entries
        unposted = db.query(JournalEntry).filter(
            and_(
                JournalEntry.entry_date <= period_end,
                JournalEntry.status != 'posted'
            )
        ).count()
        
        if unposted > 0:
            raise ValueError(f"Cannot close period: {unposted} unposted journal entries exist")
        
        # Calculate period totals
        revenue_total = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
            ChartOfAccounts.account_type == 'Revenue'
        ).scalar() or Decimal('0')
        
        expense_total = db.query(func.sum(ChartOfAccounts.current_balance)).filter(
            ChartOfAccounts.account_type == 'Expense'
        ).scalar() or Decimal('0')
        
        net_income = revenue_total - expense_total
        
        # Create closing entries
        closing_entries = []
        
        # Close revenue accounts
        revenue_accounts = db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.account_type == 'Revenue',
                ChartOfAccounts.current_balance != 0
            )
        ).all()
        
        if revenue_accounts:
            lines = []
            for account in revenue_accounts:
                lines.append({
                    'account_id': account.id,
                    'debit_amount': account.current_balance,
                    'credit_amount': Decimal('0'),
                    'description': f'Close {account.account_name}'
                })
                account.current_balance = Decimal('0')
            
            # Credit retained earnings
            retained_earnings = db.query(ChartOfAccounts).filter(
                ChartOfAccounts.account_code == '3000'
            ).first()
            if retained_earnings:
                lines.append({
                    'account_id': retained_earnings.id,
                    'debit_amount': Decimal('0'),
                    'credit_amount': revenue_total,
                    'description': 'Close revenue to retained earnings'
                })
            
            closing_entry = DoubleEntryService.create_journal_entry(
                db, {
                    'description': f'Close revenue accounts - {period_end}',
                    'entry_date': datetime.combine(period_end, datetime.min.time()),
                    'lines': lines
                }, user_id
            )
            closing_entries.append(closing_entry.id)
        
        # Close expense accounts
        expense_accounts = db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.account_type == 'Expense',
                ChartOfAccounts.current_balance != 0
            )
        ).all()
        
        if expense_accounts:
            lines = []
            for account in expense_accounts:
                lines.append({
                    'account_id': account.id,
                    'debit_amount': Decimal('0'),
                    'credit_amount': account.current_balance,
                    'description': f'Close {account.account_name}'
                })
                account.current_balance = Decimal('0')
            
            # Debit retained earnings
            retained_earnings = db.query(ChartOfAccounts).filter(
                ChartOfAccounts.account_code == '3000'
            ).first()
            if retained_earnings:
                lines.append({
                    'account_id': retained_earnings.id,
                    'debit_amount': expense_total,
                    'credit_amount': Decimal('0'),
                    'description': 'Close expenses to retained earnings'
                })
            
            closing_entry = DoubleEntryService.create_journal_entry(
                db, {
                    'description': f'Close expense accounts - {period_end}',
                    'entry_date': datetime.combine(period_end, datetime.min.time()),
                    'lines': lines
                }, user_id
            )
            closing_entries.append(closing_entry.id)
        
        db.commit()
        
        return {
            'period_end': period_end,
            'net_income': net_income,
            'revenue_total': revenue_total,
            'expense_total': expense_total,
            'closing_entries': closing_entries
        }

class MultiCurrencyService:
    """Service for multi-currency operations"""
    
    @staticmethod
    def get_exchange_rate(from_currency: str, to_currency: str, rate_date: date = None) -> Decimal:
        """Get Exchange Rate."""
        """Get exchange rate between currencies"""
        if from_currency == to_currency:
            return Decimal('1.0')
        
        # Simplified exchange rate lookup - in production, integrate with external API
        rates = {
            ('USD', 'EUR'): Decimal('0.85'),
            ('EUR', 'USD'): Decimal('1.18'),
            ('USD', 'GBP'): Decimal('0.73'),
            ('GBP', 'USD'): Decimal('1.37'),
        }
        
        return rates.get((from_currency, to_currency), Decimal('1.0'))
    
    @staticmethod
    def convert_amount(amount: Decimal, from_currency: str, to_currency: str, rate_date: date = None) -> Decimal:
        """Convert Amount."""
        """Convert amount between currencies"""
        rate = MultiCurrencyService.get_exchange_rate(from_currency, to_currency, rate_date)
        return amount * rate
    
    @staticmethod
    def create_currency_journal_entry(db: Session, amount: Decimal, from_currency: str, 
        """Create Currency Journal Entry."""
                                    to_currency: str, user_id: str) -> JournalEntry:
        """Create Currency Journal Entry."""
        """Create journal entry for currency conversion"""
        rate = MultiCurrencyService.get_exchange_rate(from_currency, to_currency)
        converted_amount = amount * rate
        
        # Get currency accounts
        from_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == f'1100-{from_currency}'
        ).first()
        to_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == f'1100-{to_currency}'
        ).first()
        
        if not from_account or not to_account:
            raise ValueError("Currency accounts not found")
        
        lines = [
            {
                'account_id': from_account.id,
                'debit_amount': Decimal('0'),
                'credit_amount': amount,
                'description': f'Convert {from_currency} to {to_currency}'
            },
            {
                'account_id': to_account.id,
                'debit_amount': converted_amount,
                'credit_amount': Decimal('0'),
                'description': f'Convert {from_currency} to {to_currency}'
            }
        ]
        
        return DoubleEntryService.create_journal_entry(
            db, {
                'description': f'Currency conversion: {amount} {from_currency} to {converted_amount} {to_currency}',
                'entry_date': datetime.now(),
                'lines': lines
            }, user_id
        )

class TaxCalculationService:
    """Service for tax calculations"""
    
    @staticmethod
    def calculate_sales_tax(amount: Decimal, tax_rate: Decimal, tax_type: str = 'sales') -> dict:
        """Calculate Sales Tax."""
        """Calculate sales tax"""
        tax_amount = amount * (tax_rate / Decimal('100'))
        return {
            'base_amount': amount,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'total_amount': amount + tax_amount,
            'tax_type': tax_type
        }
    
    @staticmethod
    def create_tax_journal_entry(db: Session, invoice_id: str, tax_calculation: dict, user_id: str) -> JournalEntry:
        """Create Tax Journal Entry."""
        """Create journal entry for tax"""
        # Get tax accounts
        sales_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == '4000'
        ).first()
        tax_payable_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == '2200'
        ).first()
        receivable_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == '1200'
        ).first()
        
        if not all([sales_account, tax_payable_account, receivable_account]):
            raise ValueError("Required tax accounts not found")
        
        lines = [
            {
                'account_id': receivable_account.id,
                'debit_amount': tax_calculation['total_amount'],
                'credit_amount': Decimal('0'),
                'description': f'Invoice with tax - {invoice_id}'
            },
            {
                'account_id': sales_account.id,
                'debit_amount': Decimal('0'),
                'credit_amount': tax_calculation['base_amount'],
                'description': f'Sales revenue - {invoice_id}'
            },
            {
                'account_id': tax_payable_account.id,
                'debit_amount': Decimal('0'),
                'credit_amount': tax_calculation['tax_amount'],
                'description': f'Sales tax payable - {invoice_id}'
            }
        ]
        
        return DoubleEntryService.create_journal_entry(
            db, {
                'description': f'Invoice with tax: {invoice_id}',
                'entry_date': datetime.now(),
                'reference': invoice_id,
                'lines': lines
            }, user_id
        )

class BankReconciliationService:
    """Service for bank reconciliation"""
    
    @staticmethod
    def reconcile_bank_statement(db: Session, bank_account_id: str, statement_data: List[dict], 
        """Reconcile Bank Statement."""
                               statement_date: date, user_id: str) -> dict:
        """Reconcile Bank Statement."""
        """Reconcile bank statement with book records"""
        # Get bank account
        bank_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == bank_account_id
        ).first()
        
        if not bank_account:
            raise ValueError("Bank account not found")
        
        # Get book balance
        book_balance = bank_account.current_balance
        
        # Calculate statement balance
        statement_balance = sum(Decimal(str(item['amount'])) for item in statement_data)
        
        # Find unmatched transactions
        unmatched_book = []
        unmatched_statement = []
        matched_transactions = []
        
        # Get book transactions for the period
        book_transactions = db.query(JournalEntryLine).join(JournalEntry).filter(
            and_(
                JournalEntryLine.account_id == bank_account_id,
                JournalEntry.entry_date <= statement_date,
                JournalEntry.status == 'posted'
            )
        ).all()
        
        # Simple matching logic (in production, use more sophisticated matching)
        for book_tx in book_transactions:
            matched = False
            for stmt_tx in statement_data:
                if (abs(book_tx.debit_amount - book_tx.credit_amount) == abs(Decimal(str(stmt_tx['amount']))) and
                    stmt_tx.get('reference') == book_tx.journal_entry.reference):
                    matched_transactions.append({
                        'book_transaction': book_tx.id,
                        'statement_transaction': stmt_tx,
                        'amount': stmt_tx['amount']
                    })
                    matched = True
                    break
            
            if not matched:
                unmatched_book.append({
                    'id': book_tx.id,
                    'amount': book_tx.debit_amount - book_tx.credit_amount,
                    'description': book_tx.description,
                    'date': book_tx.journal_entry.entry_date
                })
        
        # Find unmatched statement transactions
        matched_stmt_refs = [tx['statement_transaction'].get('reference') for tx in matched_transactions]
        for stmt_tx in statement_data:
            if stmt_tx.get('reference') not in matched_stmt_refs:
                unmatched_statement.append(stmt_tx)
        
        # Calculate reconciliation difference
        reconciliation_difference = book_balance - statement_balance
        
        return {
            'bank_account_id': bank_account_id,
            'statement_date': statement_date,
            'book_balance': book_balance,
            'statement_balance': statement_balance,
            'reconciliation_difference': reconciliation_difference,
            'matched_transactions': matched_transactions,
            'unmatched_book_transactions': unmatched_book,
            'unmatched_statement_transactions': unmatched_statement,
            'is_reconciled': abs(reconciliation_difference) <= Decimal('0.01')
        }
    
    @staticmethod
    def create_reconciliation_adjustments(db: Session, reconciliation_data: dict, user_id: str) -> List[str]:
        """Create Reconciliation Adjustments."""
        """Create journal entries for reconciliation adjustments"""
        adjustments = []
        
        # Create entries for unmatched statement transactions
        for stmt_tx in reconciliation_data['unmatched_statement_transactions']:
            lines = [
                {
                    'account_id': reconciliation_data['bank_account_id'],
                    'debit_amount': max(Decimal(str(stmt_tx['amount'])), Decimal('0')),
                    'credit_amount': max(-Decimal(str(stmt_tx['amount'])), Decimal('0')),
                    'description': f"Bank reconciliation adjustment: {stmt_tx.get('description', 'Unknown')}"
                },
                {
                    'account_id': '5000',  # Miscellaneous expense/income account
                    'debit_amount': max(-Decimal(str(stmt_tx['amount'])), Decimal('0')),
                    'credit_amount': max(Decimal(str(stmt_tx['amount'])), Decimal('0')),
                    'description': f"Bank reconciliation adjustment: {stmt_tx.get('description', 'Unknown')}"
                }
            ]
            
            adjustment = DoubleEntryService.create_journal_entry(
                db, {
                    'description': f"Bank reconciliation adjustment - {stmt_tx.get('description', 'Unknown')}",
                    'entry_date': datetime.now(),
                    'reference': stmt_tx.get('reference'),
                    'lines': lines
                }, user_id
            )
            adjustments.append(adjustment.id)
        
        return adjustments